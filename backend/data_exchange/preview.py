"""
==========================================================
NexusERP-AI  |  data_exchange  |  preview.py
==========================================================

Preview layer — read, validate, but NEVER save.

Workflow:
    Upload file
    ↓
    Read (importers.py)
    ↓
    Validate (validators.py)
    ↓
    DO NOT SAVE to main tables
    ↓
    Store validated rows in ImportLog.preview_data
    ↓
    Return preview response to client

The client then calls the confirm endpoint, which
reads ImportLog.preview_data and runs the import.

This pattern ensures:
  - File is only read once
  - Confirm step is atomic
  - User sees exactly what will be imported
==========================================================
"""

from django.utils import timezone

from .constants  import ImportStatus, MODULE_COLUMNS
from .importers  import get_importer
from .validators import get_validator
from .utils      import validate_upload
from .exceptions import MissingColumnsError, DataExchangeError


# ==========================================================
# PREVIEW ENGINE
# ==========================================================

class ImportPreviewEngine:
    """
    Orchestrates the preview phase of an import.

    Usage:
        engine = ImportPreviewEngine(company=company, module=module)
        result = engine.preview(file=uploaded_file, log=import_log)

    Result dict:
        {
            "log_id":       int,
            "total_rows":   int,
            "valid_rows":   int,
            "invalid_rows": int,
            "errors":       [{"row", "column", "message"}, ...],
            "warnings":     [{"row", "column", "message"}, ...],
            "preview":      [top 10 cleaned rows as safe dicts],
            "can_import":   bool,   # True if valid_rows > 0 and no blocking errors
        }
    """

    def __init__(self, company, module):
        self.company = company
        self.module  = module

    def preview(self, file, log):
        """
        Read the file, validate all rows, update the log, and return the
        preview dict. Does NOT save any business data.

        Args:
            file: Django uploaded file.
            log:  ImportLog instance (status=PENDING).

        Returns:
            dict: Preview result.
        """
        try:
            # Step 1: Validate the file itself (size, extension)
            validate_upload(file)

            # Step 2: Read file into raw rows
            importer = get_importer(file.name)
            raw_rows = importer.read(file)

            # Step 3: Validate all rows
            validator = get_validator(self.module, self.company)
            cleaned_rows, errors, warnings = validator.validate(raw_rows)

            # Step 4: Update the log with preview data
            total_rows   = len(raw_rows)
            failed_rows  = total_rows - len(cleaned_rows)

            log.total_rows   = total_rows
            log.valid_rows   = len(cleaned_rows)
            log.failed_rows  = failed_rows
            log.errors       = errors
            log.warnings     = warnings
            log.preview_data = self._serialise_preview_data(cleaned_rows)
            log.status       = ImportStatus.PREVIEW
            log.save()

            return {
                "log_id":       log.id,
                "total_rows":   total_rows,
                "valid_rows":   len(cleaned_rows),
                "invalid_rows": failed_rows,
                "errors":       errors,
                "warnings":     warnings,
                "preview":      self._top_preview(cleaned_rows),
                "can_import":   len(cleaned_rows) > 0 and failed_rows == 0,
            }

        except MissingColumnsError as exc:
            log.status        = ImportStatus.FAILED
            log.error_summary = exc.message
            log.errors        = [exc.to_dict()]
            log.save()
            raise

        except DataExchangeError as exc:
            log.status        = ImportStatus.FAILED
            log.error_summary = exc.message
            log.save()
            raise

        except Exception as exc:
            log.status        = ImportStatus.FAILED
            log.error_summary = f"Unexpected error during preview: {exc}"
            log.save()
            raise

    # ──────────────────────────────────────
    # SERIALISATION
    # ──────────────────────────────────────

    def _serialise_preview_data(self, cleaned_rows):
        """
        Convert cleaned rows to a JSON-serialisable format for storage.

        Model instances (Employee, Department, etc.) are replaced with
        their primary keys so they can be stored in the JSONField.
        """
        from django.db import models as django_models
        serialised = []
        for row in cleaned_rows:
            safe_row = {}
            for key, value in row.items():
                if isinstance(value, django_models.Model):
                    safe_row[f"{key}_id"] = value.pk
                elif hasattr(value, "isoformat"):
                    safe_row[key] = value.isoformat()
                elif value is None:
                    safe_row[key] = None
                else:
                    safe_row[key] = str(value) if not isinstance(value, (int, float, bool)) else value
            serialised.append(safe_row)
        return serialised

    def _top_preview(self, cleaned_rows, limit=10):
        """Return the top N cleaned rows for the API preview table."""
        return self._serialise_preview_data(cleaned_rows[:limit])
