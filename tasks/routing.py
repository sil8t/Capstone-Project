from django.urls import re_path
from . import consumers

# WebSocket URL routing
websocket_urlpatterns = [
    # Team-specific channel (used for task events: create, update, delete)
    re_path(r'^ws/tasks/(?P<team_id>\d+)/$', consumers.AppConsumer.as_asgi()),

    # User-specific channel (used for personal events like team invites)
    re_path(r'^ws/user/$', consumers.AppConsumer.as_asgi()),
]
