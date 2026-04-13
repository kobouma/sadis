# apps/orders/shipping_service.py
# Orchestre le flux d'expédition à Ouagadougou
# Chaque étape envoie un message dans le chat + notification push

from django.utils import timezone
from django.db import transaction


def get_delivery_rates() -> dict:
    """Tarifs livraison Ouagadougou depuis la BDD (configurable admin)."""
    from apps.delivery.models import DeliveryRate
    from apps.delivery.ouaga_zones import OUAGA_DELIVERY_RATES

    rates = DeliveryRate.get_active()
    result = dict(OUAGA_DELIVERY_RATES)
    result["standard"]["fee"] = rates["standard"]
    result["express"]["fee"]  = rates["express"]
    return result


def get_quartiers() -> list:
    """Liste des quartiers de Ouagadougou."""
    from apps.delivery.ouaga_zones import QUARTIERS_OUAGADOUGOU
    return sorted(QUARTIERS_OUAGADOUGOU)


@transaction.atomic
def ship_order(order, delivery_type: str, seller,
               pickup_address: str, pickup_quartier: str) -> dict:
    """
    Le vendeur confirme l'expédition.
    - Spécifie où le livreur doit récupérer le colis
    - Système crée le ticket et notifie dans le chat
    """
    from apps.orders.models import Order
    from apps.delivery.models import DeliveryTicket
    from apps.delivery.ouaga_zones import OUAGA_DELIVERY_RATES
    from apps.delivery.models import DeliveryRate

    if order.status not in [Order.Status.PAID, Order.Status.PREPARING]:
        raise ValueError("Cette commande ne peut pas être expédiée.")

    # ── Tarif ──────────────────────────────────────────────────
    rates = DeliveryRate.get_active()
    fee   = rates.get(delivery_type, rates["standard"])

    # ── Mettre à jour la commande ──────────────────────────────
    order.status        = Order.Status.SHIPPED
    order.delivery_type = delivery_type
    order.delivery_fee  = fee
    order.shipped_at    = timezone.now()
    order.save(update_fields=["status", "delivery_type",
                               "delivery_fee", "shipped_at"])

    # ── Créer le ticket ────────────────────────────────────────
    ticket = DeliveryTicket.objects.create(
        order             = order,
        delivery_type     = delivery_type,
        pickup_address    = pickup_address,
        pickup_quartier   = pickup_quartier,
        delivery_address  = order.delivery_address,
        delivery_quartier = order.delivery_city,  # quartier acheteur
        fee               = fee,
        status            = DeliveryTicket.Status.PENDING,
    )

    # ── Notifier dans le chat ──────────────────────────────────
    _chat_message(order, seller, "delivery_request", {
        "text": (
            f"📦 Votre colis est prêt ! "
            f"Livraison {_type_label(delivery_type)} depuis "
            f"*{pickup_quartier}* vers *{order.delivery_city}*. "
            f"Frais : {int(fee):,} XOF. "
            f"Un livreur va prendre en charge votre commande."
        ),
        "delivery_type":   delivery_type,
        "pickup_quartier": pickup_quartier,
        "delivery_fee":    float(fee),
        "ticket_id":       str(ticket.id),
        "step":            "shipped",
    })

    # ── Notification push acheteur ─────────────────────────────
    _notify(order.buyer, "DELIVERY_UPDATE", "📦 Colis expédié !",
            f"Votre commande « {order.product_name} » a été expédiée. "
            f"Livraison {_type_label(delivery_type)} en cours depuis {pickup_quartier}.",
            {"order_id": str(order.id), "step": "shipped"})

    # ── Notification push vendeur ──────────────────────────────
    _notify(seller, "DELIVERY_UPDATE", "✅ Expédition confirmée",
            f"Commande #{str(order.id)[:8]} expédiée. "
            f"Un livreur va récupérer le colis à {pickup_address}.",
            {"order_id": str(order.id), "step": "shipped"})

    return {"order_id": str(order.id), "ticket_id": str(ticket.id),
            "delivery_type": delivery_type, "fee": float(fee)}


@transaction.atomic
def assign_agent(ticket, agent) -> None:
    """Admin ou système assigne un livreur au ticket."""
    from apps.delivery.models import DeliveryTicket, TicketStatusHistory

    old_status = ticket.status
    ticket.status      = DeliveryTicket.Status.ASSIGNED
    ticket.agent       = agent
    ticket.assigned_at = timezone.now()
    ticket.save(update_fields=["status", "agent", "assigned_at"])

    TicketStatusHistory.objects.create(
        ticket=ticket, old_status=old_status,
        new_status=ticket.status, changed_by=agent,
        note=f"Livreur {agent.full_name} assigné"
    )

    order = ticket.order
    _chat_message(order, agent, "delivery_request", {
        "text": (
            f"🛵 Un livreur a été assigné à votre commande ! "
            f"*{agent.full_name}* va récupérer votre colis à "
            f"*{ticket.pickup_quartier}* et le livrer à *{ticket.delivery_quartier}*."
        ),
        "agent_name":      agent.full_name,
        "agent_phone":     agent.phone,
        "pickup_quartier": ticket.pickup_quartier,
        "step":            "assigned",
    })

    _notify(order.buyer, "DELIVERY_UPDATE", "🛵 Livreur assigné !",
            f"{agent.full_name} va livrer votre commande.",
            {"order_id": str(order.id), "step": "assigned"})


@transaction.atomic
def mark_picked_up(ticket, agent) -> None:
    """Livreur a récupéré le colis chez le vendeur."""
    from apps.delivery.models import DeliveryTicket, TicketStatusHistory

    old_status = ticket.status
    ticket.status       = DeliveryTicket.Status.PICKED_UP
    ticket.picked_up_at = timezone.now()
    ticket.save(update_fields=["status", "picked_up_at"])

    TicketStatusHistory.objects.create(
        ticket=ticket, old_status=old_status,
        new_status=ticket.status, changed_by=agent,
        note="Colis récupéré chez le vendeur"
    )

    order = ticket.order
    _chat_message(order, agent, "delivery_request", {
        "text": (
            f"🏃 Le livreur *{agent.full_name}* a récupéré votre colis "
            f"et est en route vers *{ticket.delivery_quartier}* !"
        ),
        "step": "picked_up",
    })

    # Mettre à jour le statut de la commande
    order.status = "delivering"
    order.save(update_fields=["status"])

    _notify(order.buyer, "DELIVERY_UPDATE", "🏃 Colis en route !",
            f"Votre commande est en route vers {ticket.delivery_quartier}. "
            f"Suivez la livraison en temps réel.",
            {"order_id": str(order.id), "step": "picked_up",
             "tracking": True})


@transaction.atomic
def mark_delivered(ticket, agent) -> None:
    """Livreur a livré le colis."""
    from apps.delivery.models import DeliveryTicket, TicketStatusHistory
    from apps.users.models import DeliveryAgent as AgentProfile

    old_status = ticket.status
    ticket.status       = DeliveryTicket.Status.DELIVERED
    ticket.delivered_at = timezone.now()
    ticket.save(update_fields=["status", "delivered_at"])

    TicketStatusHistory.objects.create(
        ticket=ticket, old_status=old_status,
        new_status=ticket.status, changed_by=agent,
        note="Colis livré"
    )

    order = ticket.order
    order.status = "delivered"
    order.save(update_fields=["status"])

    # Incrémenter le compteur du livreur
    try:
        agent_profile = agent.delivery_agent
        agent_profile.total_deliveries += 1
        agent_profile.save(update_fields=["total_deliveries"])
    except Exception:
        pass

    _chat_message(order, agent, "delivery_confirm", {
        "text": (
            f"✅ Votre colis a été livré ! "
            f"Merci d'avoir utilisé SADIS. "
            f"N'oubliez pas de laisser un avis sur le produit."
        ),
        "step": "delivered",
    })

    _notify(order.buyer, "DELIVERY_UPDATE", "✅ Colis livré !",
            f"Votre commande « {order.product_name} » a été livrée. "
            f"Merci pour votre confiance !",
            {"order_id": str(order.id), "step": "delivered"})

    _notify(order.shop.owner, "DELIVERY_UPDATE", "💰 Livraison complétée",
            f"La commande #{str(order.id)[:8]} a été livrée avec succès.",
            {"order_id": str(order.id), "step": "delivered"})


# ── Helpers internes ──────────────────────────────────────────

def _type_label(delivery_type: str) -> str:
    return {"standard": "Standard (2-6h)", "express": "Express (-2h)"}.get(
        delivery_type, delivery_type
    )


def _chat_message(order, sender, msg_type: str, payload: dict) -> None:
    """Envoie un message système dans le chat de la commande."""
    from apps.chat.models import Message
    if not order.conversation:
        return
    msg = Message.objects.create(
        conversation = order.conversation,
        sender       = sender,
        msg_type     = msg_type,
        payload      = payload,
    )
    # Broadcaster via WebSocket
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        import json
        channel_layer = get_channel_layer()
        group = f"chat_{order.conversation.id}"
        async_to_sync(channel_layer.group_send)(group, {
            "type": "chat.message",
            "message": {
                "id":          str(msg.id),
                "type":        msg.msg_type,
                "payload":     msg.payload,
                "sender_id":   str(sender.id),
                "sender_name": sender.full_name,
                "created_at":  msg.created_at.isoformat(),
            }
        })
    except Exception:
        pass  # Ne pas bloquer si Redis/channels indispo


def _notify(recipient, notif_type: str, title: str, body: str, data: dict) -> None:
    """Crée une notification push."""
    from apps.notifications.models import Notification
    Notification.objects.create(
        recipient  = recipient,
        notif_type = getattr(Notification.Type, notif_type, "DELIVERY_UPDATE"),
        title      = title,
        body       = body,
        data       = data,
    )