"""
==========================================================
NexusERP-AI  |  data_exchange  |  utils.py
==========================================================

Shared utility functions used across the Data Exchange
Framework.

Rules:
  - No business logic here.
  - No database access here.
  - Pure helper functions only.
==========================================================
"""

import io
import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from .constants import MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS
from .exceptions import (
    UnsupportedFileTypeError,
    FileTooLargeError,
)


# ==========================================================
# FILE VALIDATION
# ==========================================================

def validate_upload(file):
    """
    Validates an uploaded file's extension and size.

    Args:
        file: Django InMemoryUploadedFile or TemporaryUploadedFile

    Raises:
        UnsupportedFileTypeError: Extension not in SUPPORTED_EXTENSIONS
        FileTooLargeError:        File exceeds MAX_FILE_SIZE_MB
    """
    filename  = file.name.lower()
    extension = _get_extension(filename)

    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"File type '{extension}' is not supported. "
            f"Accepted formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise FileTooLargeError(
            f"File size ({_human_size(file.size)}) exceeds the "
            f"maximum allowed size of {MAX_FILE_SIZE_MB}MB."
        )


def _get_extension(filename):
    """Extract the lowercase file extension including the dot."""
    parts = filename.rsplit(".", 1)
    if len(parts) < 2:
        return ""
    return f".{parts[-1]}"


def _human_size(size_bytes):
    """Convert bytes to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / 1024 ** 2:.1f}MB"


# ==========================================================
# DATA TYPE COERCION
# ==========================================================

def parse_date(value, row=None, column=None):
    """
    Parse a date value from an Excel cell or CSV string.

    Accepts:
        - Python date / datetime objects (from Excel)
        - Strings in YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY

    Returns:
        datetime.date or None if value is empty.

    Raises:
        ValueError with a descriptive message on bad format.
    """
    if value is None or str(value).strip() == "":
        return None

    if isinstance(value, (date, datetime)):
        return value.date() if isinstance(value, datetime) else value

    value_str = str(value).strip()
    formats   = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]

    for fmt in formats:
        try:
            return datetime.strptime(value_str, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        f"Invalid date '{value_str}'. "
        "Expected formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY"
    )


def parse_time(value, row=None, column=None):
    """
    Parse a time value from an Excel cell or CSV string.

    Accepts:
        - Python time objects
        - Strings in HH:MM or HH:MM:SS

    Returns:
        datetime.time or None if empty.
    """
    from datetime import time as time_type

    if value is None or str(value).strip() == "":
        return None

    if isinstance(value, time_type):
        return value

    # Excel sometimes stores time as a float fraction of 24 hours
    if isinstance(value, float):
        total_seconds = int(round(value * 86400))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return time_type(hours % 24, minutes, seconds)

    value_str = str(value).strip()
    for fmt in ["%H:%M:%S", "%H:%M"]:
        try:
            return datetime.strptime(value_str, fmt).time()
        except ValueError:
            continue

    raise ValueError(
        f"Invalid time '{value_str}'. Expected HH:MM or HH:MM:SS."
    )


def parse_decimal(value, row=None, column=None):
    """
    Parse a decimal/monetary value.

    Returns:
        Decimal or None if empty.

    Raises:
        ValueError on unparseable input.
    """
    if value is None or str(value).strip() == "":
        return None

    try:
        return Decimal(str(value).strip().replace(",", ""))
    except InvalidOperation:
        raise ValueError(
            f"Invalid numeric value '{value}'. Expected a number."
        )


def parse_int(value, row=None, column=None):
    """Parse an integer value."""
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid integer value '{value}'."
        )


def parse_bool(value, row=None, column=None):
    """
    Parse a boolean-ish value from Excel/CSV.
    Accepts: Yes/No, True/False, 1/0, y/n
    """
    if value is None or str(value).strip() == "":
        return False

    lowered = str(value).strip().lower()
    if lowered in ("yes", "true", "1", "y"):
        return True
    if lowered in ("no", "false", "0", "n"):
        return False

    raise ValueError(
        f"Invalid boolean value '{value}'. Use Yes/No or True/False."
    )


def clean_string(value):
    """Strip whitespace from a string; return empty string for None."""
    if value is None:
        return ""
    return str(value).strip()


# ==========================================================
# STRUCTURED ERROR BUILDERS
# ==========================================================

def make_error(row, column, message):
    """Build a single structured error dict."""
    return {
        "row":     row,
        "column":  column,
        "message": message,
    }


def make_warning(row, column, message):
    """Build a single structured warning dict."""
    return {
        "row":     row,
        "column":  column,
        "message": message,
    }


# ==========================================================
# NORMALISATION
# ==========================================================

def normalise_header(header):
    """
    Normalise a column header from an uploaded file.
    Converts to lowercase, strips whitespace, replaces
    spaces with underscores so headers match constants.

    Example:
        "First Name " → "first_name"
        "Employee ID" → "employee_id"
    """
    return str(header).strip().lower().replace(" ", "_")


def normalise_headers(headers):
    """Apply normalise_header to a list of headers."""
    return [normalise_header(h) for h in headers]
