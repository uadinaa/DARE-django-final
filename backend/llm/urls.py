from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from llm.serializers import CreateAssistantSerializer, UpdateAssistantResponseSerializer

from .views import (
    ConversationHistoryViewSet,
    CreateAssistantView,
    UpdateAssistantResponseView,
)


class WSCreateDocView(APIView):
    @swagger_auto_schema(
        operation_description="Документация WS: ws://…/ws/assistant/create/\n"
        "Принимает payload: { message: string }\n"
        "Возвращает: { message: string, thread_id: string }",
        request_body=CreateAssistantSerializer,
        responses={
            200: openapi.Response(description="WS отвечает JSON с message и thread_id")
        },
    )
    def post(self, request):
        return Response(status=204)


class WSUpdateDocView(APIView):
    @swagger_auto_schema(
        operation_description="Документация WS: ws://…/ws/assistant/update/\n"
        "Принимает payload: { message: string, thread_id: string }\n"
        "Возвращает: { response: string }",
        request_body=UpdateAssistantResponseSerializer,
        responses={
            200: openapi.Response(description="WS возвращает JSON с полем response")
        },
    )
    def post(self, request):
        return Response(status=204)


router = DefaultRouter()
router.register(
    r"conversation-history/(?P<thread_id>\w+)",
    ConversationHistoryViewSet,
    basename="conversation-history",
)

router.register(r"assistant/create", CreateAssistantView, basename="create_assistant")
router.register(
    r"assistant/update",
    UpdateAssistantResponseView,
    basename="update_assistant_response",
)

urlpatterns = [
    path("", include(router.urls)),
    path("docs/ws/assistant/create/", WSCreateDocView.as_view(), name="ws-create-doc"),
    path("docs/ws/assistant/update/", WSUpdateDocView.as_view(), name="ws-update-doc"),
]
