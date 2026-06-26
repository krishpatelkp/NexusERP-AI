"""
==========================================================
NexusERP-AI Attendance Constants
==========================================================

Single source of truth for all attendance configuration.

Business thresholds are defined here so that:
- Services import from one place
- Future company-level overrides require one change
- No magic numbers anywhere in the codebase
==========================================================
"""


# ==========================================================
# ATTENDANCE CALCULATION THRESHOLDS
# ==========================================================

FULL_DAY_MINUTES = 480
# 8 hours = Full day present

HALF_DAY_MINUTES = 240
# 4 hours = Half day present

# Below HALF_DAY_MINUTES = Absent


# ==========================================================
# REPORT DEFAULTS
# ==========================================================

DEFAULT_REPORT_PAGE_SIZE = 25
# Attendance reports show 25 records per page

DEFAULT_HISTORY_MONTHS = 6
# Employee attendance history defaults to last 6 months


# ==========================================================
# GRACE PERIOD
# ==========================================================

MAX_GRACE_MINUTES = 120
# Maximum allowed grace period for any shift

MIN_GRACE_MINUTES = 0
# Minimum allowed grace period