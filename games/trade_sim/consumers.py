"""
TradeSim WebSocket Consumers
Real-time multiplayer game communication
"""
import json
from typing import Union
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()


class GameConsumer(AsyncWebsocketConsumer):
    """
    Main game WebSocket consumer for real-time multiplayer
    """

    user: Union[User, AnonymousUser, None]  # type: ignore

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = "game_world"
        self.room_group_name = f"game_{self.room_name}"
        self.user = self.scope.get("user", AnonymousUser())

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send connection success message
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "message": "Connected to TradeSim server",
                }
            )
        )

        # Notify others about new player
        user_id = getattr(self.user, "id", None)
        if not isinstance(self.user, AnonymousUser) and user_id is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "player_joined",
                    "player_id": user_id,
                    "username": getattr(self.user, "username", "Unknown"),
                },
            )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Notify others about player leaving
        user_id = getattr(self.user, "id", None)
        if not isinstance(self.user, AnonymousUser) and user_id is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "player_left",
                    "player_id": user_id,
                    "username": getattr(self.user, "username", "Unknown"),
                },
            )
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")
            # Route message based on type
            if message_type == "player:move":
                await self.handle_player_move(data)
            elif message_type == "chat:message":
                await self.handle_chat_message(data)
            elif message_type == "trade:request":
                await self.handle_trade_request(data)
            elif message_type == "ping":
                await self.handle_ping(data)
            else:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )
                )
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "Invalid JSON"})
            )
        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def handle_player_move(self, data):
        """Handle player movement"""
        position = data.get("position", [0, 0, 0])
        rotation = data.get("rotation", 0)
        user_id = getattr(self.user, "id", None)
        if not isinstance(self.user, AnonymousUser) and user_id is not None:
            await self.update_player_position(user_id, position, rotation)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "player_move_broadcast",
                "player_id": user_id,
                "position": position,
                "rotation": rotation,
            },
        )

    async def handle_chat_message(self, data):
        """Handle chat messages"""
        message = data.get("message", "")
        room = data.get("room", "global")
        if not message.strip():
            return
        msg_id = None
        user_id = getattr(self.user, "id", None)
        username = "Guest"
        if not isinstance(self.user, AnonymousUser) and user_id is not None:
            msg_id = await self.save_chat_message(user_id, room, message)
            username = getattr(self.user, "username", "Unknown")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message_broadcast",
                "message_id": msg_id,
                "user_id": user_id,
                "username": username,
                "room": room,
                "message": message,
                "timestamp": None,  # Will be added by frontend
            },
        )

    async def handle_trade_request(self, data):
        """Handle trade requests"""
        from_city = data.get("from_city")
        to_city = data.get("to_city")
        product_id = data.get("product_id")
        amount = data.get("amount", 1)

        try:
            # Execute trade
            result = await self.execute_trade(from_city, to_city, product_id, amount)

            # Send result to requesting player
            await self.send(
                text_data=json.dumps(
                    {"type": "trade:result", "success": True, "result": result}
                )
            )

            # Broadcast market update to all players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "market_update_broadcast",
                    "from_city": from_city,
                    "to_city": to_city,
                    "product_id": product_id,
                },
            )

        except Exception as e:
            await self.send(
                text_data=json.dumps(
                    {"type": "trade:result", "success": False, "error": str(e)}
                )
            )

    async def handle_ping(self, data):
        """Handle ping for latency measurement"""
        await self.send(
            text_data=json.dumps({"type": "pong", "timestamp": data.get("timestamp")})
        )

    # Broadcast handlers

    async def player_joined(self, event):
        """Broadcast when player joins"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "player:joined",
                    "player_id": event["player_id"],
                    "username": event["username"],
                }
            )
        )

    async def player_left(self, event):
        """Broadcast when player leaves"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "player:left",
                    "player_id": event["player_id"],
                    "username": event["username"],
                }
            )
        )

    async def player_move_broadcast(self, event):
        """Broadcast player movement"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "player:move",
                    "player_id": event["player_id"],
                    "position": event["position"],
                    "rotation": event["rotation"],
                }
            )
        )

    async def chat_message_broadcast(self, event):
        """Broadcast chat message"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat:message",
                    "message_id": event["message_id"],
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "room": event["room"],
                    "message": event["message"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def market_update_broadcast(self, event):
        """Broadcast market updates"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "market:update",
                    "from_city": event["from_city"],
                    "to_city": event["to_city"],
                    "product_id": event["product_id"],
                }
            )
        )

    async def notification_broadcast(self, event):
        """Broadcast notifications"""
        await self.send(
            text_data=json.dumps(
                {"type": "notification", "notification": event["notification"]}
            )
        )

    # Database operations

    @database_sync_to_async
    def update_player_position(self, user_id, position, rotation):
        """Update player position in database"""
        from .models import Character

        try:
            character = Character.objects.filter(user_id=user_id).first()
            if character:
                character.choices["position"] = position
                character.choices["rotation"] = rotation
                character.save(update_fields=["choices"])
        except Exception as e:
            print(f"Error updating player position: {e}")

    @database_sync_to_async
    def save_chat_message(self, user_id, room, message):
        """Save chat message to database"""
        from .models import ChatMessage
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
            msg = ChatMessage.objects.create(user=user, room=room, message=message)
            return msg.pk  # Use pk instead of id for better compatibility
        except Exception as e:
            print(f"Error saving chat message: {e}")
            return None

    @database_sync_to_async
    def execute_trade(self, from_city, to_city, product_id, amount):
        """Execute trade between cities"""
        from .services import process_city_trade
        from .models import City, Product

        try:
            from_city_obj = City.objects.get(id=from_city)
            to_city_obj = City.objects.get(id=to_city)
            product_obj = Product.objects.get(id=product_id)

            result = process_city_trade(from_city_obj, to_city_obj, product_obj, amount)
            return result
        except Exception as e:
            raise Exception(f"Trade failed: {str(e)}")


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Dedicated consumer for notifications
    """

    user: Union[User, AnonymousUser, None]  # type: ignore

    async def connect(self):
        """Connect to notification channel"""
        self.user = self.scope.get("user", AnonymousUser())

        if isinstance(self.user, AnonymousUser) or not hasattr(self.user, "id") or not self.user.id:  # type: ignore
            await self.close()
            return

        self.user_group_name = f"notifications_{self.user.id}"  # type: ignore

        # Join user-specific notification group
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """Disconnect from notification channel"""
        if not isinstance(self.user, AnonymousUser):
            await self.channel_layer.group_discard(
                self.user_group_name, self.channel_name
            )

    async def send_notification(self, event):
        """Send notification to user"""
        await self.send(
            text_data=json.dumps({"type": "notification", "data": event["data"]})
        )
