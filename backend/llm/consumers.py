import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from llama_index.agent.openai import OpenAIAssistantAgent

from .models import ConversationHistory
from core import settings


logger = logging.getLogger("platform")


class CreateAssistantConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Убираем проверку аутентификации
        await self.accept()
        logger.info(f"WS connected: CreateAssistantConsumer for user {self.scope['user'].username if self.scope['user'].is_authenticated else 'anonymous'}")

    async def receive_json(self, content):
        message = content.get("message")
        if not message:
            return await self.send_json({"error": 'Поле "message" обязательно'})

        try:
            agent = OpenAIAssistantAgent.from_existing(assistant_id=settings.ASSISTANT_ID, verbose=True)
            resp = agent.chat(message)

            # Сохранение в БД с пользователем (если он аутентифицирован)
            await sync_to_async(ConversationHistory.objects.create)(
                user_message=message,
                assistant_response=resp.response,
                thread_id=agent.thread_id,
                user=self.scope["user"] if self.scope["user"].is_authenticated else None
            )

            await self.send_json(
                {"message": resp.response, "thread_id": agent.thread_id}
            )

        except Exception as e:
            logger.error(f"CreateAssistantConsumer error: {e}")
            await self.send_json({"error": str(e)})


class UpdateAssistantConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Убираем проверку аутентификации
        await self.accept()
        logger.info(f"WS connected: UpdateAssistantConsumer for user {self.scope['user'].username if self.scope['user'].is_authenticated else 'anonymous'}")

    async def receive_json(self, content):
        message = content.get("message")
        thread_id = content.get("thread_id")
        if not message or not thread_id:
            return await self.send_json(
                {"error": "Нужны оба поля: message и thread_id"}
            )

        try:
            agent = OpenAIAssistantAgent.from_existing(
                assistant_id=settings.ASSISTANT_ID, thread_id=thread_id, verbose=True
            )
            resp = agent.chat(message)

            await sync_to_async(ConversationHistory.objects.create)(
                user_message=message,
                assistant_response=resp.response,
                thread_id=thread_id,
                user=self.scope["user"] if self.scope["user"].is_authenticated else None
            )

            await self.send_json({"response": resp.response})

        except Exception as e:
            logger.error(f"UpdateAssistantConsumer error: {e}")
            await self.send_json({"error": str(e)})

