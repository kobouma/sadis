import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user            = self.scope["user"]
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name      = f"chat_{self.conversation_id}"
        if isinstance(self.user, AnonymousUser):
            await self.close(code=4001); return
        if not await self._is_participant():
            await self.close(code=4003); return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self._mark_unread()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data     = json.loads(text_data)
            msg_type = data.get("type", "text")
            payload  = data.get("payload", {})
        except json.JSONDecodeError:
            await self._send_error("Format JSON invalide."); return
        from .models import MessageType
        if msg_type not in [t.value for t in MessageType]:
            await self._send_error(f"Type inconnu : {msg_type}"); return
        message = await self._save_message(msg_type, payload)
        await self._side_effects(msg_type, payload)
        await self.channel_layer.group_send(self.group_name, {
            "type": "chat.message", "message": await self._serialize(message)})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def _is_participant(self):
        from .models import Conversation
        try:
            conv = Conversation.objects.get(pk=self.conversation_id)
            return self.user in (conv.buyer, conv.seller)
        except Conversation.DoesNotExist: return False

    @database_sync_to_async
    def _save_message(self, msg_type, payload):
        from .models import Message, Conversation
        conv = Conversation.objects.get(pk=self.conversation_id)
        return Message.objects.create(conversation=conv, sender=self.user,
                                      msg_type=msg_type, payload=payload)

    @database_sync_to_async
    def _serialize(self, message):
        return {"id": str(message.id), "type": message.msg_type, "payload": message.payload,
                "sender_id": str(message.sender.id), "sender_name": message.sender.full_name,
                "created_at": message.created_at.isoformat()}

    @database_sync_to_async
    def _mark_unread(self):
        from .models import Message
        Message.objects.filter(conversation_id=self.conversation_id,
                               is_read=False).exclude(sender=self.user).update(is_read=True)

    @database_sync_to_async
    def _side_effects(self, msg_type, payload):
        from .models import Conversation, ConversationStatus
        conv = Conversation.objects.get(pk=self.conversation_id)
        if msg_type == "escrow_held":
            conv.escrow_amount = payload.get("amount", 0)
            conv.status = ConversationStatus.ESCROW
        elif msg_type in ["escrow_released", "delivery_confirm"]:
            conv.escrow_amount = 0; conv.status = ConversationStatus.CLOSED
        elif msg_type == "payment":  conv.status = ConversationStatus.PAID
        elif msg_type == "dispute":  conv.status = ConversationStatus.DISPUTED
        conv.save()

    async def _send_error(self, message):
        await self.send(text_data=json.dumps({"type": "error", "payload": {"message": message}}))
