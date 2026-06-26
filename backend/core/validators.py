"""
==========================================================
NexusERP-AI Core Validators
==========================================================

This module contains reusable validation functions
shared across multiple applications.

Rules:

- Validators must be generic.
- Validators must not depend on a specific model.
- Business-specific validation belongs
  inside the respective application.

Examples:

✓ validate_non_empty_string()
✓ validate_positive_number()
✓ validate_company_isolation()

NOT

✗ validate_shift_overlap()
✗ validate_payroll_lock()

==========================================================
"""

from rest_framework import serializers

def validate_non_empty_string(
    value,
    field_name,
):
    """
    Validate that a string is not empty.

    Returns the stripped value.
    """

    value = value.strip()

    if not value:

        raise serializers.ValidationError(
            f"{field_name} cannot be empty."
        )

    return value


def validate_non_empty_uppercase_string(
    value,
    field_name,
):
    """
    Validate a required uppercase string.
    """

    value = value.strip().upper()

    if not value:

        raise serializers.ValidationError(
            f"{field_name} cannot be empty."
        )

    return value


def validate_trimmed_string(
    value,
):
    """
    Strip leading and trailing spaces.
    """

    return value.strip()