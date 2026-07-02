"""
==========================================================
NexusERP-AI  |  data_exchange  |  admin.py
==========================================================
"""

from django.contrib import admin
from .models import ImportLog, ExportLog

@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "module", "status", "original_filename", "total_rows", "imported_rows", "started_at")
    list_filter = ("status", "module", "company")
    search_fields = ("original_filename", "company__company_name")
    readonly_fields = ("started_at", "completed_at", "duration_seconds")

@admin.register(ExportLog)
class ExportLogAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "module", "export_format", "status", "total_rows", "created_at")
    list_filter = ("status", "module", "export_format", "company")
    search_fields = ("company__company_name",)
    readonly_fields = ("created_at", "duration_seconds")
