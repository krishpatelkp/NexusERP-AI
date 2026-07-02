"""
==========================================================
NexusERP-AI  |  data_exchange  |  urls.py
==========================================================
"""

from django.urls import path
from .views import (
    ImportPreviewAPIView,
    ImportConfirmAPIView,
    ImportCancelAPIView,
    DownloadTemplateAPIView,
    ImportHistoryAPIView,
    ExportAPIView,
)

app_name = "data_exchange"

urlpatterns = [
    path("import/preview/", ImportPreviewAPIView.as_view(), name="import-preview"),
    path("import/confirm/", ImportConfirmAPIView.as_view(), name="import-confirm"),
    path("import/cancel/<int:log_id>/", ImportCancelAPIView.as_view(), name="import-cancel"),
    path("import/template/<str:module>/", DownloadTemplateAPIView.as_view(), name="download-template"),
    path("import/history/", ImportHistoryAPIView.as_view(), name="import-history"),
    path("export/", ExportAPIView.as_view(), name="export"),
]
