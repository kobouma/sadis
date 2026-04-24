def notify(recipient, notif_type, title, body, data=None):
    from .models import Notification
    return Notification.objects.create(recipient=recipient, notif_type=notif_type,
                                       title=title, body=body, data=data or {})

def notify_many(recipients, **kwargs):
    return [notify(r, **kwargs) for r in recipients]
