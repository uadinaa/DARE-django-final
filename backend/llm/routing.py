from django.urls import re_path

from .consumers import CreateAssistantConsumer, UpdateAssistantConsumer

websocket_urlpatterns = [
    re_path(r"ws/assistant/create/$", CreateAssistantConsumer.as_asgi()),
    re_path(r"ws/assistant/update/$", UpdateAssistantConsumer.as_asgi()),
]
