# apps/tracking/consumers.py
# WebSocket temps réel — position du livreur + étapes de livraison

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone


class TrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket wss://sadis.onrender.com/ws/tracking/<order_id>/

    Événements reçus (livreur → serveur) :
      { "type": "location", "latitude": 12.36, "longitude": -1.53 }
      { "type": "picked_up" }
      { "type": "delivered" }

    Événements envoyés (serveur → acheteur/vendeur) :
      { "type": "location",    "latitude": .., "longitude": .., "agent_name": .., "timestamp": .. }
      { "type": "status",      "status": "picked_up"|"delivered", "message": "..", "timestamp": .. }
      { "type": "ticket_info", ...infos initiales du ticket... }
    """

    async def connect(self):
        self.user     = self.scope["user"]
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.group    = f"tracking_{self.order_id}"

        if isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return

        if not await self._can_access():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        # Envoyer les infos initiales du ticket
        ticket_data = await self._get_ticket_info()
        if ticket_data:
            await self.send(text_data=json.dumps({
                "type":    "ticket_info",
                "payload": ticket_data,
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        """Seul le livreur assigné peut envoyer des mises à jour."""
        if not await self._is_agent():
            return

        try:
            data     = json.loads(text_data)
            evt_type = data.get("type")
        except (json.JSONDecodeError, KeyError):
            return

        if evt_type == "location":
            # Mise à jour position GPS
            try:
                lat = float(data["latitude"])
                lng = float(data["longitude"])
            except (KeyError, ValueError):
                return

            await self._update_location(lat, lng)
            await self.channel_layer.group_send(self.group, {
                "type":       "tracking.location",
                "latitude":   lat,
                "longitude":  lng,
                "agent_name": self.user.full_name,
                "timestamp":  timezone.now().isoformat(),
            })

        elif evt_type == "picked_up":
            # Livreur a récupéré le colis
            await self._mark_picked_up()
            await self.channel_layer.group_send(self.group, {
                "type":    "tracking.status",
                "status":  "picked_up",
                "message": f"📦 {self.user.full_name} a récupéré le colis et est en route !",
                "timestamp": timezone.now().isoformat(),
            })

        elif evt_type == "delivered":
            # Livreur a livré
            await self._mark_delivered()
            await self.channel_layer.group_send(self.group, {
                "type":    "tracking.status",
                "status":  "delivered",
                "message": "✅ Colis livré avec succès !",
                "timestamp": timezone.now().isoformat(),
            })

        elif evt_type == "online":
            # Livreur se connecte / disponible
            await self._set_online(True)

        elif evt_type == "offline":
            await self._set_online(False)

    # ── Handlers groupe ───────────────────────────────────────

    async def tracking_location(self, event):
        await self.send(text_data=json.dumps({
            "type":       "location",
            "latitude":   event["latitude"],
            "longitude":  event["longitude"],
            "agent_name": event["agent_name"],
            "timestamp":  event["timestamp"],
        }))

    async def tracking_status(self, event):
        await self.send(text_data=json.dumps({
            "type":      "status",
            "status":    event["status"],
            "message":   event["message"],
            "timestamp": event["timestamp"],
        }))

    # ── DB helpers ────────────────────────────────────────────

    @database_sync_to_async
    def _can_access(self):
        from apps.orders.models import Order
        try:
            order = Order.objects.select_related(
                "buyer", "delivery_ticket__agent"
            ).get(pk=self.order_id)
            agent = getattr(
                getattr(order, "delivery_ticket", None), "agent", None
            )
            # Acheteur, vendeur ou livreur peuvent suivre
            return self.user in [order.buyer, order.shop.owner, agent]
        except Order.DoesNotExist:
            return False

    @database_sync_to_async
    def _is_agent(self):
        from apps.orders.models import Order
        try:
            ticket = Order.objects.get(pk=self.order_id).delivery_ticket
            return ticket.agent == self.user
        except (Order.DoesNotExist, AttributeError):
            return False

    @database_sync_to_async
    def _get_ticket_info(self):
        from apps.delivery.models import DeliveryTicket
        try:
            ticket = DeliveryTicket.objects.select_related(
                "agent", "order__buyer", "order__shop"
            ).get(order_id=self.order_id)
            return {
                "ticket_id":          str(ticket.id),
                "status":             ticket.status,
                "delivery_type":      ticket.delivery_type,
                "pickup_quartier":    ticket.pickup_quartier,
                "delivery_quartier":  ticket.delivery_quartier,
                "agent_name":  ticket.agent.full_name if ticket.agent else None,
                "agent_phone": ticket.agent.phone     if ticket.agent else None,
                "agent_lat":   float(ticket.agent_latitude)  if ticket.agent_latitude  else None,
                "agent_lng":   float(ticket.agent_longitude) if ticket.agent_longitude else None,
                "fee":         float(ticket.fee),
            }
        except DeliveryTicket.DoesNotExist:
            return None

    @database_sync_to_async
    def _update_location(self, lat, lng):
        from apps.delivery.models import DeliveryTicket
        DeliveryTicket.objects.filter(order_id=self.order_id).update(
            agent_latitude=lat, agent_longitude=lng
        )

    @database_sync_to_async
    def _mark_picked_up(self):
        from apps.delivery.models import DeliveryTicket
        from apps.orders.shipping_service import mark_picked_up
        try:
            ticket = DeliveryTicket.objects.get(order_id=self.order_id)
            mark_picked_up(ticket, self.user)
        except Exception:
            pass

    @database_sync_to_async
    def _mark_delivered(self):
        from apps.delivery.models import DeliveryTicket
        from apps.orders.shipping_service import mark_delivered
        try:
            ticket = DeliveryTicket.objects.get(order_id=self.order_id)
            mark_delivered(ticket, self.user)
        except Exception:
            pass

    @database_sync_to_async
    def _set_online(self, online: bool):
        try:
            self.user.delivery_agent.is_online = online
            self.user.delivery_agent.save(update_fields=["is_online"])
        except Exception:
            pass