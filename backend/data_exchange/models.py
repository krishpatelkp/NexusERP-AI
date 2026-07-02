"""
==========================================================
NexusERP-AI  |  data_exchange  |  models.py
==========================================================

Audit models for the Data Exchange Framework.

Design Principles:
  - Every import/export is permanently logged.
  - Logs are immutable historical records.
  - AI, dashboards and auditors can query logs.
  - Never delete logs — use status to track lifecycle.
  - preview_data stores the validated rows as JSON
    so the confirm step does not re-read the file.
==========================================================
"""

from django.db import models
from django.conf import settings

from company.models import Company
from .constants import ImportModule, ExportModule, ImportStatus, ExportStatus, ExportFormat


# ==========================================================
# IMPORT LOG
# ==========================================================

class ImportLog(models.Model):
    """
    Permanent audit record for every import attempt.

    Lifecycle:
        PENDING    → File uploaded, not yet validated
        PREVIEW    → Validation complete, awaiting confirmation
        PROCESSING → Transaction in progress
        COMPLETED  → All rows imported successfully
        FAILED     → Import failed (see error_summary)
        CANCELLED  → User cancelled after preview

    The preview_data JSON field stores validated rows
    between the preview and confirm steps.
    This avoids re-reading the file on confirm.

    AI Readiness:
        - errors JSON enables AI to answer "why did it fail?"
        - All counts are stored explicitly for analytics
        - duration_seconds enables performance monitoring
    """

    # ──────────────────────────────────────
    # IDENTITY
    # ──────────────────────────────────────

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="import_logs",
        help_text="Company that performed the import.",
    )

    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="import_logs",
        help_text="User who initiated the import.",
    )

    # ──────────────────────────────────────
    # MODULE & FILE
    # ──────────────────────────────────────

    module = models.CharField(
        max_length=20,
        choices=ImportModule.CHOICES,
        db_index=True,
        help_text="Which ERP module this import targets.",
    )

    original_filename = models.CharField(
        max_length=255,
        help_text="Original filename uploaded by the user.",
    )

    file_size_bytes = models.PositiveIntegerField(
        default=0,
        help_text="Size of the uploaded file in bytes.",
    )

    # ──────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=ImportStatus.CHOICES,
        default=ImportStatus.PENDING,
        db_index=True,
    )

    # ──────────────────────────────────────
    # ROW COUNTS
    # ──────────────────────────────────────

    total_rows = models.PositiveIntegerField(
        default=0,
        help_text="Total data rows in the uploaded file.",
    )

    valid_rows = models.PositiveIntegerField(
        default=0,
        help_text="Rows that passed all validation checks.",
    )

    failed_rows = models.PositiveIntegerField(
        default=0,
        help_text="Rows that failed one or more validation checks.",
    )

    imported_rows = models.PositiveIntegerField(
        default=0,
        help_text="Rows actually written to the database.",
    )

    # ──────────────────────────────────────
    # VALIDATION & ERROR DATA
    # ──────────────────────────────────────

    errors = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Structured list of row-level validation errors. "
            "Format: [{row, column, message}, ...]"
        ),
    )

    warnings = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Non-blocking warnings found during validation. "
            "Import can proceed despite warnings."
        ),
    )

    preview_data = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Validated and cleaned rows stored between preview "
            "and confirm steps. Cleared after import."
        ),
    )

    error_summary = models.TextField(
        blank=True,
        default="",
        help_text="Top-level error message if the whole import failed.",
    )

    # ──────────────────────────────────────
    # TIMING
    # ──────────────────────────────────────

    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the import was initiated.",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the import finished (success or failure).",
    )

    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Total time taken to complete the import.",
    )

    # ──────────────────────────────────────
    # META
    # ──────────────────────────────────────

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Import Log"
        verbose_name_plural = "Import Logs"
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["module"]),
            models.Index(fields=["status"]),
            models.Index(fields=["started_at"]),
        ]

    def __str__(self):
        return (
            f"[{self.module.upper()}] "
            f"{self.original_filename} "
            f"({self.status}) "
            f"by {self.imported_by}"
        )

    # ──────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────

    @property
    def success_rate(self):
        """Percentage of rows successfully imported."""
        if not self.total_rows:
            return 0
        return round((self.imported_rows / self.total_rows) * 100, 2)

    @property
    def has_errors(self):
        return bool(self.errors)

    @property
    def is_preview_ready(self):
        return self.status == "preview"


# ==========================================================
# EXPORT LOG
# ==========================================================

class ExportLog(models.Model):
    """
    Permanent audit record for every export.

    AI Readiness:
        - What module was exported?
        - Who exported it?
        - Which format?
        - How many rows?
        - When?
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="export_logs",
    )

    exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="export_logs",
    )

    module = models.CharField(
        max_length=20,
        choices=ExportModule.CHOICES,
        db_index=True,
    )

    export_format = models.CharField(
        max_length=10,
        choices=ExportFormat.CHOICES,
        default=ExportFormat.EXCEL,
    )

    status = models.CharField(
        max_length=20,
        choices=ExportStatus.CHOICES,
        default=ExportStatus.PENDING,
    )

    total_rows = models.PositiveIntegerField(
        default=0,
    )

    filters_applied = models.JSONField(
        default=dict,
        blank=True,
        help_text="Query filters used when generating this export.",
    )

    error_message = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    duration_seconds = models.FloatField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Export Log"
        verbose_name_plural = "Export Logs"
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["module"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"[{self.module.upper()}] "
            f"{self.export_format.upper()} "
            f"by {self.exported_by} "
            f"({self.status})"
        )
