"""
==========================================================
NexusERP-AI  |  data_exchange  |  serializers.py
==========================================================

Serializers for import/export API requests and responses.
"""

from rest_framework import serializers
from .models import ImportLog, ExportLog
from .constants import ImportModule, ExportModule, ExportFormat

class ImportPreviewRequestSerializer(serializers.Serializer):
    """Validator for the file upload preview request."""
    module = serializers.ChoiceField(choices=ImportModule.CHOICES)
    file = serializers.FileField()

class ImportConfirmRequestSerializer(serializers.Serializer):
    """Validator for the confirm request."""
    log_id = serializers.IntegerField()

class ExportRequestSerializer(serializers.Serializer):
    """Validator for export requests."""
    module = serializers.ChoiceField(choices=ExportModule.CHOICES)
    format = serializers.ChoiceField(choices=ExportFormat.CHOICES, default=ExportFormat.EXCEL)
    # The frontend can send other filters dynamically
    
class ImportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportLog
        fields = (
            "id", "module", "original_filename", "status",
            "total_rows", "valid_rows", "failed_rows", "imported_rows",
            "errors", "warnings", "started_at", "completed_at", "duration_seconds",
            "error_summary", "success_rate"
        )

class ExportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportLog
        fields = "__all__"
