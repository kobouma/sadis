from celery import shared_task

@shared_task
def notify_chat_message(conversation_id, sender_id):
    from apps.chat.models import Conversation
    from apps.users.models import User
    from .utils import notify
    from .models import Notification
    try:
        conv      = Conversation.objects.get(pk=conversation_id)
        sender    = User.objects.get(pk=sender_id)
        recipient = conv.seller if sender == conv.buyer else conv.buyer
        notify(recipient=recipient, notif_type=Notification.Type.CHAT_MESSAGE,
               title=f"Message de {sender.full_name}", body="Vous avez un nouveau message.",
               data={"conversation_id": str(conversation_id)})
    except Exception: pass

@shared_task
def release_escrow(conversation_id):
    from apps.chat.models import Conversation, ConversationStatus
    try:
        conv = Conversation.objects.get(pk=conversation_id)
        conv.escrow_amount = 0
        conv.status = ConversationStatus.CLOSED
        conv.save()
    except Exception: pass