from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChatRequestSerializer
from .services import AIService


class AIChatAPIView(APIView):
    """
    POST /api/ai/chat/

    Accepts a natural language question and returns
    an AI-generated response backed by ERP data.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        history  = serializer.validated_data.get(
            "conversation_history", []
        )

        service = AIService()

        result = service.chat(
            question=question,
            company=request.user.company,
            user=request.user,
            conversation_history=history,
        )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )


class AIHealthCheckAPIView(APIView):
    """
    GET /api/ai/health/

    Returns whether Ollama is reachable.
    Useful for the React frontend to show
    AI availability status.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        from ai.llm.ollama_client import OllamaClient
        from ai.constants import OLLAMA_MODEL

        client = OllamaClient()
        available = client.is_available()

        return Response(
            {
                "ollama_available": available,
                "model":            OLLAMA_MODEL,
                "status":           "online" if available else "offline",
            },
            status=status.HTTP_200_OK,
        )