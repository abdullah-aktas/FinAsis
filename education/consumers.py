from __future__ import annotations

from typing import Any, Dict
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Meeting, MeetingPresence
from django.core.cache import cache
import time


class MeetingConsumer(AsyncJsonWebsocketConsumer):
    """
    Lightweight signaling server for P2P WebRTC using Channels.

    Protocol (JSON):
      { "type": "join|leave|offer|answer|ice|chat",
        "from": "clientId",
        "to": "optionalTargetClientId",
        "data": { ... } }

    Room is derived from URL kwarg: room_name.
    We broadcast to the room and let clients filter by `to` on the client side.
    """

    async def connect(self) -> None:
        route = self.scope.get("url_route", {})  # type: ignore[assignment]
        kwargs = route.get("kwargs", {}) if isinstance(route, dict) else {}
        self.room_name = kwargs.get("room_name", "default")
        self.group_name = f"meeting_{self.room_name}"

        # AuthZ: only organizer/participant can join
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(code=4401)  # unauthorized
            return

        if not await self._user_can_join(int(self.room_name)):
            await self.close(code=4403)  # forbidden
            return

        # Locked room check
        try:
            meeting_id = int(self.room_name)
            if cache.get(f"meeting_lock_{meeting_id}"):
                await self.close(code=4403)
                return
        except Exception:
            pass

        # Create presence row and join group
        await self._mark_presence_join()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # init simple rate limiter state
        self._rl_window_start = time.monotonic()
        self._rl_count = 0

    async def disconnect(self, close_code: int) -> None:  # noqa: ARG002
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self._mark_presence_leave()

    async def receive_json(
        self, content: Dict[str, Any], **kwargs: Any
    ) -> None:  # noqa: ANN401
        # Basic schema validation and rate limiting
        now = time.monotonic()
        window = getattr(self, "_rl_window_start", now)
        count = getattr(self, "_rl_count", 0)
        if now - window > 10.0:
            # reset 10s window
            self._rl_window_start = now
            self._rl_count = 0
        else:
            self._rl_count = count + 1
            if self._rl_count > 60:
                # too many messages in 10s; drop silently
                return

        # Normalize and fan out
        msg_type = content.get("type")
        if msg_type not in {
            "join",
            "leave",
            "offer",
            "answer",
            "ice",
            "chat",
            "moderate",
            "whiteboard",
            "hand",
            "cobrowse",
        }:
            return
        user = self.scope.get("user")
        user_id = getattr(user, "pk", None)
        # Authorization: moderate messages only from organizer
        if msg_type == "moderate" and not await self._is_organizer():
            return
        # Handle server-side state changes
        if msg_type == "moderate":
            data = content.get("data") or {}
            action = data.get("action")
            if action == "lock-room":
                self._set_room_lock(True)
            elif action == "unlock-room":
                self._set_room_lock(False)
            elif action == "set-presenter":
                # organizer assigns presenter user_id
                raw_uid = data.get("user_id") if isinstance(data, dict) else None
                uid: int | None = None
                if isinstance(raw_uid, int):
                    uid = raw_uid
                elif isinstance(raw_uid, str):
                    try:
                        uid = int(raw_uid)
                    except Exception:
                        uid = None
                if uid is not None:
                    await self._set_presenter(uid)
            elif action == "clear-presenter":
                await self._set_presenter(None)
        # Authorization for co-browsing: only organizer or presenter can emit
        if msg_type == "cobrowse" and not await self._is_presenter_or_organizer():
            return

        # Clamp payload sizes
        data = content.get("data")
        if isinstance(data, dict) and "text" in data:
            # limit chat messages to 500 chars
            try:
                txt = data.get("text")
                if isinstance(txt, str) and len(txt) > 500:
                    data["text"] = txt[:500]
            except Exception:
                pass
        payload: Dict[str, Any] = {
            "type": msg_type,
            "from": user_id,
            "to": content.get("to"),
            "data": data
            if isinstance(data, (dict, list, str, int, float, type(None)))
            else None,
        }
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "broadcast", "payload": payload, "sender": self.channel_name},
        )

    async def broadcast(self, event: Dict[str, Any]) -> None:
        # Do not echo to sender
        if event.get("sender") == self.channel_name:
            return
        await self.send_json(event["payload"])

    @database_sync_to_async
    def _user_can_join(self, meeting_id: int) -> bool:
        user = self.scope.get("user")
        try:
            meeting = (
                Meeting.objects.select_related("organizer")
                .prefetch_related("participants")
                .get(pk=meeting_id)
            )
        except Meeting.DoesNotExist:
            return False
        if not user or isinstance(user, AnonymousUser):
            return False
        if user == meeting.organizer:
            return True
        user_pk = getattr(user, "pk", None)
        if user_pk is None:
            return False
        return meeting.participants.filter(pk=user_pk).exists()

    @database_sync_to_async
    def _is_organizer(self) -> bool:
        user = self.scope.get("user")
        try:
            meeting_id = int(self.room_name)
            meeting = Meeting.objects.only("id", "organizer_id").get(pk=meeting_id)
        except Exception:
            return False
        if not user or isinstance(user, AnonymousUser):
            return False
        try:
            org_pk = meeting.organizer.pk  # type: ignore[attr-defined]
        except Exception:
            org_pk = None
        return getattr(user, "pk", None) == org_pk

    def _set_room_lock(self, locked: bool) -> None:
        try:
            meeting_id = int(self.room_name)
        except Exception:
            return
        cache.set(f"meeting_lock_{meeting_id}", bool(locked), timeout=None)

    @database_sync_to_async
    def _set_presenter(self, user_id: int | None) -> None:
        try:
            meeting_id = int(self.room_name)
        except Exception:
            return
        try:
            meeting = Meeting.objects.only("id").get(pk=meeting_id)
        except Meeting.DoesNotExist:
            return
        # None clears presenter
        setattr(meeting, "presenter_id", user_id)
        meeting.save(update_fields=["presenter"])

    @database_sync_to_async
    def _is_presenter_or_organizer(self) -> bool:
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser):
            return False
        try:
            meeting_id = int(self.room_name)
            meeting = Meeting.objects.only("id", "organizer_id", "presenter_id").get(
                pk=meeting_id
            )
        except Exception:
            return False
        uid = getattr(user, "pk", None)
        if uid is None:
            return False
        try:
            if uid == meeting.organizer_id:  # type: ignore[attr-defined]
                return True
        except Exception:
            pass
        try:
            if uid == meeting.presenter_id:  # type: ignore[attr-defined]
                return True
        except Exception:
            pass
        return False

    @database_sync_to_async
    def _mark_presence_join(self) -> None:
        user = self.scope.get("user")
        try:
            meeting_id = int(self.room_name)
        except Exception:
            return
        if not user or not getattr(user, "pk", None):
            return
        MeetingPresence.objects.create(
            meeting_id=meeting_id, user_id=user.pk, client_id=self.channel_name
        )

    @database_sync_to_async
    def _mark_presence_leave(self) -> None:
        user = self.scope.get("user")
        try:
            meeting_id = int(self.room_name)
        except Exception:
            return
        if not user or not getattr(user, "pk", None):
            return
        qs = MeetingPresence.objects.filter(
            meeting_id=meeting_id,
            user_id=user.pk,
            client_id=self.channel_name,
            left_at__isnull=True,
        ).order_by("-joined_at")
        obj = qs.first()
        if obj:
            from django.utils import timezone

            obj.left_at = timezone.now()
            obj.save(update_fields=["left_at"])
