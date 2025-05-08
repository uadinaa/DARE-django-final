import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from llama_index.agent.openai import OpenAIAssistantAgent

from .models import ConversationHistory

logger = logging.getLogger("platform")


class CreateAssistantConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info("WS connected: CreateAssistantConsumer")

    async def receive_json(self, content):
        message = content.get("message")
        if not message:
            return await self.send_json({"error": 'Поле "message" обязательно'})

        try:
            agent = OpenAIAssistantAgent.from_existing(assistant_id="...", verbose=True)
            resp = agent.chat(message)

            # Сохранение в БД
            await sync_to_async(ConversationHistory.objects.create)(
                user_message=message,
                assistant_response=resp.response,
                thread_id=agent.thread_id,
            )

            await self.send_json(
                {"message": resp.response, "thread_id": agent.thread_id}
            )

        except Exception as e:
            logger.error(f"CreateAssistantConsumer error: {e}")
            await self.send_json({"error": str(e)})


class UpdateAssistantConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info("WS connected: UpdateAssistantConsumer")

    async def receive_json(self, content):
        message = content.get("message")
        thread_id = content.get("thread_id")
        if not message or not thread_id:
            return await self.send_json(
                {"error": "Нужны оба поля: message и thread_id"}
            )

        try:
            agent = OpenAIAssistantAgent.from_existing(
                assistant_id="...", thread_id=thread_id, verbose=True
            )
            resp = agent.chat(message)

            await sync_to_async(ConversationHistory.objects.create)(
                user_message=message,
                assistant_response=resp.response,
                thread_id=thread_id,
            )

            await self.send_json({"response": resp.response})

        except Exception as e:
            logger.error(f"UpdateAssistantConsumer error: {e}")
            await self.send_json({"error": str(e)})
