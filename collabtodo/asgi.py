import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import tasks.routing  # 👈 your app's routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collabtodo.settings')
django.setup()  # ✅ only needed if you use things like database access in consumers

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            tasks.routing.websocket_urlpatterns
        )
    ),
})
