import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

class TrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user     = self.scope["user"]
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.group    = f"tracking_{self.order_id}"
        if isinstance(self.user, AnonymousUser):
            await self.close(code=4001); return
        if not await self._can_access():
            await self.close(code=4003); return
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        if not await self._is_agent(): return
        try:
            data = json.loads(text_data)
            lat, lng = float(data["latitude"]), float(data["longitude"])
        except (json.JSONDecodeError, KeyError, ValueError): return
        await self._update_location(lat, lng)
        await self.channel_layer.group_send(self.group, {
            "type": "location.update", "latitude": lat, "longitude": lng,
            "agent_name": self.user.full_name, "timestamp": timezone.now().isoformat()})

    async def location_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "location", "latitude": event["latitude"], "longitude": event["longitude"],
            "agent_name": event["agent_name"], "timestamp": event["timestamp"]}))

    @database_sync_to_async
    def _can_access(self):
        from apps.orders.models import Order
        try:
            order  = Order.objects.select_related("buyer","delivery_ticket__agent").get(pk=self.order_id)
            agent  = getattr(getattr(order, "delivery_ticket", None), "agent", None)
            return self.user in [order.buyer, agent]
        except Order.DoesNotExist: return False

    @database_sync_to_async
    def _is_agent(self):
        from apps.orders.models import Order
        try: return Order.objects.get(pk=self.order_id).delivery_ticket.agent == self.user
        except (Order.DoesNotExist, AttributeError): return False

    @database_sync_to_async
    def _update_location(self, lat, lng):
        from apps.delivery.models import DeliveryTicket
        DeliveryTicket.objects.filter(order_id=self.order_id).update(
            agent_latitude=lat, agent_longitude=lng)
