from django.urls import re_path
from .consumers import TrackingConsumer
tracking_websocket_urlpatterns = [
    re_path(r"ws/tracking/(?P<order_id>[^/]+)/$", TrackingConsumer.as_asgi()),
]