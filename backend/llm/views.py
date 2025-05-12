import logging

from llama_index.agent.openai import OpenAIAssistantAgent
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import ConversationHistory
from .serializers import (
    ConversationHistorySerializer,
    CreateAssistantSerializer,
    UpdateAssistantResponseSerializer,
)
from core import settings

logger = logging.getLogger("platform")


class CreateAssistantView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ConversationHistory.objects.all()
    serializer_class = CreateAssistantSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        logger.info("Received request to CreateAssistantView")
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Validation failed: {serializer.errors}")
                return Response(
                    {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )
            message = serializer.validated_data["message"]
            logger.debug(f"User message: {message}")

            chatgpt_agent = OpenAIAssistantAgent.from_existing(
                assistant_id=settings.ASSISTANT_ID,
                verbose=True,
            )
            response = chatgpt_agent.chat(message)
            logger.info("Assistant responded successfully")

            ConversationHistory.objects.create(
                user_message=message,
                assistant_response=response.response,
                thread_id=chatgpt_agent.thread_id,
                user=request.user
            )
            return Response(
                {"message": response.response, "thread_id": chatgpt_agent.thread_id},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Error in CreateAssistantView: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateAssistantResponseView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ConversationHistory.objects.all()
    serializer_class = UpdateAssistantResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        logger.info("Received request to UpdateAssistantResponseView")
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Validation failed: {serializer.errors}")
                return Response(
                    {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )

            message = serializer.validated_data["message"]
            thread_id = serializer.validated_data["thread_id"]
            logger.debug(f"User message: {message}, Thread ID: {thread_id}")

            chatgpt_agent = OpenAIAssistantAgent.from_existing(
                assistant_id=settings.ASSISTANT_ID,
                thread_id=thread_id,
                verbose=True,
            )
            response = chatgpt_agent.chat(message)
            logger.info("Assistant response updated successfully")

            ConversationHistory.objects.create(
                user_message=message,
                assistant_response=response.response,
                thread_id=thread_id,
                user=request.user
            )
            return Response({"response": response.response}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in UpdateAssistantResponseView: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Возвращаем историю только для текущего пользователя
        return ConversationHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_thread(self, request):
        thread_id = request.query_params.get('thread_id')
        if not thread_id:
            return Response({"error": "thread_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        conversations = self.get_queryset().filter(thread_id=thread_id)
        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data)
