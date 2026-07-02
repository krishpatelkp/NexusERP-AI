"""
==========================================================
NexusERP-AI  |  data_exchange  |  exceptions.py
==========================================================

Custom exception hierarchy for the Data Exchange
Framework.

Design Rules:
- All exceptions are structured (carry row/column context)
- All exceptions are serialisable for API responses
- Never raise generic Python exceptions from services
==========================================================
"""


# ==========================================================
# BASE
# ==========================================================

class DataExchangeError(Exception):
    """
    Base exception for all data exchange errors.

    Carries a human-readable message plus optional
    context (row number, column name) so the API
    can return a structured error response.
    """

    def __init__(self, message, row=None, column=None):
        super().__init__(message)
        self.message = message
        self.row     = row
        self.column  = column

    def to_dict(self):
        """Return a serialisable dict suitable for API responses."""
        result = {"message": self.message}
        if self.row is not None:
            result["row"] = self.row
        if self.column is not None:
            result["column"] = self.column
        return result


# ==========================================================
# FILE ERRORS
# ==========================================================

class UnsupportedFileTypeError(DataExchangeError):
    """Raised when the uploaded file extension is not supported."""


class FileTooLargeError(DataExchangeError):
    """Raised when the uploaded file exceeds the allowed size limit."""


class EmptyFileError(DataExchangeError):
    """Raised when the uploaded file contains no data rows."""


class TooManyRowsError(DataExchangeError):
    """Raised when the uploaded file exceeds MAX_IMPORT_ROWS."""


class MalformedFileError(DataExchangeError):
    """Raised when the file cannot be parsed (corrupt, wrong format, etc.)."""


# ==========================================================
# COLUMN / HEADER ERRORS
# ==========================================================

class MissingColumnsError(DataExchangeError):
    """
    Raised when one or more required columns are absent.

    Attributes:
        missing (list[str]): Column names that are absent.
    """

    def __init__(self, missing):
        self.missing = missing
        message = (
            f"Missing required columns: {', '.join(missing)}. "
            "Please use the official template."
        )
        super().__init__(message)

    def to_dict(self):
        return {
            "message": self.message,
            "missing_columns": self.missing,
        }


# ==========================================================
# ROW / VALIDATION ERRORS
# ==========================================================

class RowValidationError(DataExchangeError):
    """
    Raised for a single invalid row during validation.

    The validator collects these and returns them all
    at once so the user sees every error in one response.
    """


class DuplicateValueError(RowValidationError):
    """Raised when a unique field (employee_id, asset_tag) is duplicated."""


class ForeignKeyNotFoundError(RowValidationError):
    """
    Raised when a FK reference (department, designation,
    leave_type, vendor, category) cannot be resolved.
    """


class CompanyIsolationError(DataExchangeError):
    """
    Raised when a row references a record that belongs
    to a different company.

    This is a security violation and must always be logged.
    """


# ==========================================================
# IMPORT ERRORS
# ==========================================================

class PreviewExpiredError(DataExchangeError):
    """
    Raised when a confirm request references a preview
    log that has already been imported or cancelled.
    """


class ImportAlreadyConfirmedError(DataExchangeError):
    """
    Raised when a confirm is attempted on an already
    completed import log.
    """


class ImportServiceError(DataExchangeError):
    """
    Raised when the import service encounters an
    unexpected error during transaction execution.
    """


# ==========================================================
# EXPORT ERRORS
# ==========================================================

class ExportError(DataExchangeError):
    """Raised when export generation fails."""


class UnsupportedExportFormatError(DataExchangeError):
    """Raised when an unsupported export format is requested."""
