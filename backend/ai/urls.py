from django.urls import path
from .views import AIChatAPIView, AIHealthCheckAPIView

urlpatterns = [
    path(
        "chat/",
        AIChatAPIView.as_view(),
        name="ai-chat",
    ),
    path(
        "health/",
        AIHealthCheckAPIView.as_view(),
        name="ai-health",
    ),
]