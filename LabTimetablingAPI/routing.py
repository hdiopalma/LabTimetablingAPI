# websocket url patterns

from django.urls import re_path, path
from scheduling_data.utils.consumers import NotificationConsumer


websocket_urlpatterns = [
    #websocket for solution status updates
    re_path(r'ws/notification/', NotificationConsumer.as_asgi()),
    # path('ws/notification/', NotificationConsumer.as_asgi())
]
