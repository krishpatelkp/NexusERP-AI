from django.db import models


# ==========================================================
# LEAVE STATUS
# ==========================================================

class LeaveStatus(
    models.TextChoices,
):
    """
    Lifecycle of a leave request.
    """

    PENDING = (
        "Pending",
        "Pending",
    )

    APPROVED = (
        "Approved",
        "Approved",
    )

    REJECTED = (
        "Rejected",
        "Rejected",
    )

    CANCELLED = (
        "Cancelled",
        "Cancelled",
    )


# ==========================================================
# APPROVAL STATUS
# ==========================================================

class ApprovalStatus(
    models.TextChoices,
):
    """
    HR / Manager approval status.
    """

    PENDING = (
        "Pending",
        "Pending",
    )

    APPROVED = (
        "Approved",
        "Approved",
    )

    REJECTED = (
        "Rejected",
        "Rejected",
    )


# ==========================================================
# LEAVE REQUEST SOURCE
# ==========================================================

class LeaveSource(
    models.TextChoices,
):
    """
    Source from which the leave request
    was created.
    """

    WEB = (
        "Web",
        "Web",
    )

    MOBILE = (
        "Mobile",
        "Mobile",
    )

    API = (
        "API",
        "API",
    )

    ADMIN = (
        "Admin",
        "Admin",
    )