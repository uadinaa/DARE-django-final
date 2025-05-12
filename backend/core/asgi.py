import os
import django
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Инициализируем Django перед импортом middleware
django.setup()

# Импортируем после django.setup()
from llm.middleware import JWTAuthMiddleware
import llm.routing

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(
            AuthMiddlewareStack(URLRouter(llm.routing.websocket_urlpatterns))
        ),
    }
)
