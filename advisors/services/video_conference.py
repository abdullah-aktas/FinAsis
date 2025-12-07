# -*- coding: utf-8 -*-
"""
Video Konferans Servisleri
Mali Müşavir - Müşteri online görüşmeleri için
"""
import time
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse
from abc import ABC, abstractmethod


class VideoConferenceProvider(ABC):
    """Video konferans sağlayıcı soyut sınıfı"""

    @abstractmethod
    def create_meeting(self, topic, start_time, duration_minutes, **kwargs) -> dict:
        """Yeni görüşme oluştur"""
        pass

    @abstractmethod
    def get_meeting(self, meeting_id) -> dict:
        """Görüşme detaylarını getir"""
        pass

    @abstractmethod
    def delete_meeting(self, meeting_id) -> bool:
        """Görüşmeyi iptal et"""
        pass


class FinasisMeetingProvider(VideoConferenceProvider):
    """
    FinAsis Eğitim modülü üzerinden dahili toplantılar
    """

    def __init__(self):
        base = getattr(settings, "FINASIS_MEETING_BASE_URL", "") or getattr(
            settings, "SITE_BASE_URL", ""
        )
        self.base_url = (base or "").rstrip("/")

    def _build_join_url(self, meeting_id: int) -> str:
        path = reverse("education:meetings_detail", args=[meeting_id])
        if self.base_url:
            return f"{self.base_url}{path}"
        return path

    def create_meeting(self, topic, start_time, duration_minutes, **kwargs) -> dict:
        from education.models import Meeting

        organizer = kwargs.get("organizer")
        if organizer is None:
            raise ValueError("FinAsis toplantıları için organizer zorunludur.")

        description = kwargs.get("description") or ""
        participants = kwargs.get("participants") or []

        end_time = start_time + timedelta(minutes=duration_minutes)
        meeting = Meeting.objects.create(
            title=topic,
            description=description,
            organizer=organizer,
            meeting_type="online",
            status="scheduled",
            start_time=start_time,
            end_time=end_time,
            presenter=organizer,
        )
        if participants:
            meeting.participants.add(*participants)

        meeting.join_url = self._build_join_url(meeting.pk)
        meeting.save(update_fields=["join_url"])

        return {
            "meeting_id": str(meeting.pk),
            "meeting_url": meeting.join_url,
            "provider": "finasis",
            "education_meeting_id": meeting.pk,
        }

    def get_meeting(self, meeting_id) -> dict:
        from education.models import Meeting

        meeting = Meeting.objects.filter(pk=meeting_id).first()
        if not meeting:
            raise Exception("FinAsis toplantısı bulunamadı.")
        return {
            "meeting_id": str(meeting.pk),
            "status": meeting.status,
            "meeting_url": meeting.join_url,
            "start_time": meeting.start_time,
            "end_time": meeting.end_time,
        }

    def delete_meeting(self, meeting_id) -> bool:
        from education.models import Meeting

        meeting = Meeting.objects.filter(pk=meeting_id).first()
        if not meeting:
            return True
        meeting.status = "canceled"
        meeting.join_url = ""
        meeting.save(update_fields=["status", "join_url"])
        return True


class ZoomProvider(VideoConferenceProvider):
    """
    Zoom Video Konferans Entegrasyonu

    Gerekli ayarlar (settings.py):
    ZOOM_API_KEY = 'your-api-key'
    ZOOM_API_SECRET = 'your-api-secret'
    ZOOM_USER_ID = 'your-zoom-user-id'
    """

    def __init__(self):
        self.api_key = getattr(settings, "ZOOM_API_KEY", "")
        self.api_secret = getattr(settings, "ZOOM_API_SECRET", "")
        self.user_id = getattr(settings, "ZOOM_USER_ID", "")
        self.base_url = "https://api.zoom.us/v2"

    def _generate_jwt_token(self):
        """JWT token oluştur (Zoom API için)"""
        # Not: Zoom artık Server-to-Server OAuth kullanıyor
        # Bu basitleştirilmiş bir örnek
        # Gerçek implementasyonda OAuth 2.0 kullanılmalı
        import jwt

        payload = {"iss": self.api_key, "exp": datetime.utcnow() + timedelta(hours=1)}

        token = jwt.encode(payload, self.api_secret, algorithm="HS256")
        return token

    def create_meeting(self, topic, start_time, duration_minutes, **kwargs):
        """
        Zoom toplantısı oluştur

        Args:
            topic: Toplantı konusu
            start_time: Başlangıç zamanı (datetime)
            duration_minutes: Süre (dakika)
            **kwargs: Ek parametreler

        Returns:
            dict: Toplantı bilgileri
        """
        url = f"{self.base_url}/users/{self.user_id}/meetings"

        headers = {
            "Authorization": f"Bearer {self._generate_jwt_token()}",
            "Content-Type": "application/json",
        }

        # Timezone aware datetime'ı UTC string'e çevir
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        data = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time_str,
            "duration": duration_minutes,
            "timezone": kwargs.get("timezone", "Europe/Istanbul"),
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": True,
                "audio": "voip",
                "auto_recording": kwargs.get("auto_recording", "none"),
            },
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            meeting_data = response.json()

            return {
                "meeting_id": str(meeting_data["id"]),
                "meeting_url": meeting_data["join_url"],
                "password": meeting_data.get("password", ""),
                "host_email": meeting_data.get("host_email", ""),
                "start_url": meeting_data.get("start_url", ""),
                "provider": "zoom",
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Zoom toplantısı oluşturulamadı: {str(e)}")

    def get_meeting(self, meeting_id):
        """Toplantı detaylarını getir"""
        url = f"{self.base_url}/meetings/{meeting_id}"

        headers = {"Authorization": f"Bearer {self._generate_jwt_token()}"}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Zoom toplantısı alınamadı: {str(e)}")

    def delete_meeting(self, meeting_id):
        """Toplantıyı iptal et"""
        url = f"{self.base_url}/meetings/{meeting_id}"

        headers = {"Authorization": f"Bearer {self._generate_jwt_token()}"}

        try:
            response = requests.delete(url, headers=headers, timeout=30)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"Zoom toplantısı silinemedi: {str(e)}")


class JitsiProvider(VideoConferenceProvider):
    """
    Jitsi Meet Entegrasyonu (Self-hosted veya meet.jit.si)

    Gerekli ayarlar (settings.py):
    JITSI_DOMAIN = 'meet.jit.si'  # veya kendi domain'iniz
    JITSI_APP_ID = 'your-app-id'  # opsiyonel
    JITSI_APP_SECRET = 'your-app-secret'  # opsiyonel
    """

    def __init__(self):
        self.domain = getattr(settings, "JITSI_DOMAIN", "meet.jit.si")
        self.app_id = getattr(settings, "JITSI_APP_ID", "")
        self.app_secret = getattr(settings, "JITSI_APP_SECRET", "")

    def _generate_room_name(self, topic):
        """Oda adı oluştur"""
        # URL-safe oda adı oluştur
        import re

        room_name = re.sub(r"[^a-zA-Z0-9]", "", topic)
        timestamp = int(time.time())
        return f"FinAsis_{room_name}_{timestamp}"

    def _generate_jwt_token(self, room_name, user_name, moderator=False):
        """JWT token oluştur (Jitsi için)"""
        if not self.app_id or not self.app_secret:
            return None

        import jwt

        payload = {
            "iss": self.app_id,
            "aud": self.app_id,
            "exp": datetime.utcnow() + timedelta(hours=2),
            "nbf": datetime.utcnow(),
            "room": room_name,
            "context": {
                "user": {"name": user_name, "moderator": str(moderator).lower()}
            },
        }

        token = jwt.encode(payload, self.app_secret, algorithm="HS256")
        return token

    def create_meeting(self, topic, start_time, duration_minutes, **kwargs):
        """
        Jitsi toplantısı oluştur

        Not: Jitsi instant meeting'leri destekler, scheduled değil.
        Oda adı ve URL oluşturulur.
        """
        room_name = self._generate_room_name(topic)

        # Host için JWT token (eğer credentials varsa)
        host_name = kwargs.get("host_name", "Host")
        host_token = self._generate_jwt_token(room_name, host_name, moderator=True)

        # Temel URL
        base_url = f"https://{self.domain}/{room_name}"

        # JWT token varsa URL'ye ekle
        if host_token:
            meeting_url = f"{base_url}?jwt={host_token}"
        else:
            meeting_url = base_url

        return {
            "meeting_id": room_name,
            "meeting_url": meeting_url,
            "password": "",  # Jitsi varsayılan olarak şifre kullanmaz
            "room_name": room_name,
            "provider": "jitsi",
        }

    def get_meeting(self, meeting_id):
        """
        Toplantı detaylarını getir

        Not: Jitsi meet.jit.si için API yok, room bilgileri döner
        """
        return {
            "room_name": meeting_id,
            "url": f"https://{self.domain}/{meeting_id}",
            "status": "created",
        }

    def delete_meeting(self, meeting_id):
        """
        Toplantıyı iptal et

        Not: Jitsi instant meeting, silmeye gerek yok
        """
        return True


class GoogleMeetProvider(VideoConferenceProvider):
    """
    Google Meet Entegrasyonu

    Gerekli ayarlar (settings.py):
    GOOGLE_CALENDAR_API_KEY = 'your-api-key'
    GOOGLE_SERVICE_ACCOUNT_FILE = 'path/to/service-account.json'
    """

    def __init__(self):
        self.service_account_file = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", "")

    def create_meeting(self, topic, start_time, duration_minutes, **kwargs):
        """
        Google Meet toplantısı oluştur (Google Calendar API ile)
        """
        # Google Calendar API kullanarak event oluştur
        # Meet link otomatik oluşturulur

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=["https://www.googleapis.com/auth/calendar"],
            )

            service = build("calendar", "v3", credentials=credentials)

            end_time = start_time + timedelta(minutes=duration_minutes)

            event = {
                "summary": topic,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": kwargs.get("timezone", "Europe/Istanbul"),
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": kwargs.get("timezone", "Europe/Istanbul"),
                },
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"finasis-{int(time.time())}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
                "attendees": kwargs.get("attendees", []),
            }

            created_event = (
                service.events()
                .insert(calendarId="primary", body=event, conferenceDataVersion=1)
                .execute()
            )

            meet_link = created_event["conferenceData"]["entryPoints"][0]["uri"]

            return {
                "meeting_id": created_event["id"],
                "meeting_url": meet_link,
                "password": "",
                "provider": "google_meet",
            }

        except Exception as e:
            raise Exception(f"Google Meet toplantısı oluşturulamadı: {str(e)}")

    def get_meeting(self, meeting_id) -> dict:
        """Toplantı detaylarını getir"""
        # Google Calendar API kullanarak event detaylarını getir
        return {"meeting_id": meeting_id, "status": "active"}

    def delete_meeting(self, meeting_id) -> bool:
        """Toplantıyı iptal et"""
        # Google Calendar API kullanarak event'i sil
        return True


class VideoConferenceFactory:
    """Video konferans servisi factory"""

    _providers = {
        "finasis": FinasisMeetingProvider,
        "zoom": ZoomProvider,
        "jitsi": JitsiProvider,
        "google_meet": GoogleMeetProvider,
    }

    @classmethod
    def get_provider(cls, provider_name=None):
        """
        Video konferans sağlayıcısı al

        Args:
            provider_name: Sağlayıcı adı ('zoom', 'jitsi', 'google_meet')
                          None ise ayarlardan varsayılan alınır

        Returns:
            VideoConferenceProvider: Sağlayıcı instance
        """
        if provider_name is None:
            provider_name = getattr(settings, "DEFAULT_VIDEO_PROVIDER", "finasis")

        provider_class = cls._providers.get(provider_name.lower())

        if not provider_class:
            raise ValueError(
                f"Desteklenmeyen video konferans sağlayıcısı: {provider_name}"
            )

        return provider_class()

    @classmethod
    def create_consultation_meeting(cls, booking, provider_name=None):
        """
        Danışmanlık randevusu için toplantı oluştur

        Args:
            booking: ConsultationBooking instance
            provider_name: Sağlayıcı adı (opsiyonel)

        Returns:
            dict: Toplantı bilgileri
        """
        selected_provider = provider_name or getattr(booking, "video_provider", None)
        provider = cls.get_provider(selected_provider)
        organizer_user = getattr(
            getattr(getattr(booking, "consultant", None), "advisor", None), "user", None
        )
        if organizer_user is None:
            raise ValueError("Randevu için mali müşavir hesabı bulunamadı.")
        participants = []
        if getattr(booking, "client_id", None):
            participants.append(booking.client)

        # Randevu bilgileriyle toplantı oluştur
        import pytz
        from datetime import datetime

        # Randevu tarih ve saatini birleştir
        tz = pytz.timezone(booking.timezone)
        scheduled_datetime = datetime.combine(
            booking.scheduled_date, booking.scheduled_time
        )
        scheduled_datetime = tz.localize(scheduled_datetime)

        topic = f"{booking.subject} - {booking.consultant.display_name}"

        meeting_data = provider.create_meeting(
            topic=topic,
            start_time=scheduled_datetime,
            duration_minutes=booking.duration_minutes,
            timezone=booking.timezone,
            host_name=booking.consultant.display_name,
            organizer=organizer_user,
            participants=participants,
            description=booking.description,
            booking=booking,
        )

        # Randevuya meeting bilgilerini kaydet
        booking.meeting_url = meeting_data.get("meeting_url", "")
        booking.meeting_id = meeting_data.get("meeting_id", "")
        booking.meeting_password = meeting_data.get("password", "")

        update_fields = {"meeting_url", "meeting_id", "meeting_password"}

        provider_label = meeting_data.get("provider")
        if provider_label and hasattr(booking, "video_provider"):
            booking.video_provider = provider_label
            update_fields.add("video_provider")

        education_meeting_id = meeting_data.get("education_meeting_id")
        if education_meeting_id and hasattr(booking, "education_meeting_id"):
            booking.education_meeting_id = education_meeting_id
            update_fields.add("education_meeting")

        booking.save(update_fields=list(update_fields))

        return meeting_data


# Helper fonksiyonlar
def create_meeting_for_booking(booking, provider_name=None):
    """Randevu için toplantı oluştur (kolaylık fonksiyonu)"""
    return VideoConferenceFactory.create_consultation_meeting(
        booking, provider_name=provider_name
    )


def cancel_meeting_for_booking(booking, provider_name=None):
    """Randevu toplantısını iptal et"""
    if not booking.meeting_id:
        return

    try:
        provider = VideoConferenceFactory.get_provider(
            provider_name or getattr(booking, "video_provider", None)
        )
        provider.delete_meeting(booking.meeting_id)
    except Exception as e:
        # Hata loglama
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Toplantı iptal edilemedi: {str(e)}")
