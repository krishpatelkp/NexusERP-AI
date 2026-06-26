"""
==========================================================
NexusERP-AI Engineering Standards (NES)
==========================================================

NES-001
Immutable business fields must never change.

NES-002
Company isolation is mandatory.

NES-003
Historical business data must never be overwritten.

NES-004
Soft delete is preferred over hard delete.

NES-005
Every API must enforce permissions.

NES-006
Every module must be AI-ready.

NES-007
Business validation belongs in models.

NES-008
Serializers validate API input only.

NES-009
No business logic inside views.

NES-010
Reusable code belongs in core.

==========================================================
"""

"""
==========================================================
NexusERP-AI Global Constants
==========================================================
"""

# ==========================================================
# FILE UPLOADS
# ==========================================================

MAX_DOCUMENT_FILE_SIZE_MB = 10

ALLOWED_DOCUMENT_EXTENSIONS = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
)

# ==========================================================
# VALIDATION
# ==========================================================

MAX_GRACE_MINUTES = 120

MIN_GRACE_MINUTES = 0

# ==========================================================
# PAGINATION
# ==========================================================

DEFAULT_PAGE_SIZE = 20

MAX_PAGE_SIZE = 100