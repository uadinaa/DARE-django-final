from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async
import django
from django.apps import apps

class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Получаем токен из заголовков
        headers = dict(scope["headers"])
        auth_header = headers.get(b"authorization", b"").decode()
        
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Декодируем токен
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                user = await self.get_user(user_id)
                scope["user"] = user
            except Exception as e:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)

    @staticmethod
    async def get_user(user_id):
        try:
            # Используем apps.get_model вместо прямого импорта
            User = apps.get_model('auth', 'User')
            return await sync_to_async(User.objects.get)(id=user_id)
        except Exception:
            return AnonymousUser() 