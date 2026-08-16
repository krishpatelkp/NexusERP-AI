"""
==========================================================
NexusERP-AI — Tool Registration
==========================================================

All tools are registered here.
The planner imports the registry from this module.

To add a new tool:
    1. Create the tool class in the appropriate file.
    2. Import it here.
    3. Call registry.register(YourTool).
==========================================================
"""

from ai.tools.registry import registry

from ai.tools.employee_tools import (
    EmployeeSummaryTool,
    EmployeesByDepartmentTool,
    EmployeeRegisterTool,
)

from ai.tools.attendance_tools import (
    AttendanceDashboardTool,
    AttendanceSummaryTool,
    AttendanceExceptionsTool,
)

from ai.tools.leave_tools import (
    LeaveSummaryTool,
    LeaveBalanceTool,
    PendingLeavesTool,
)

from ai.tools.payroll_tools import (
    PayrollSummaryTool,
    PayrollRegisterTool,
    DepartmentSalaryCostTool,
)

from ai.tools.inventory_tools import (
    InventorySummaryTool,
    AssignedAssetsTool,
    MaintenanceHistoryTool,
)

from ai.tools.payment_tools import (
    PaymentSummaryTool,
    PendingPaymentsTool,
)

from ai.tools.report_tools import (
    HeadcountTrendTool,
    PayrollTrendTool,
    MaintenanceCostTrendTool,
)

# ── Employee Tools ──────────────────────────────────────
registry.register(EmployeeSummaryTool)
registry.register(EmployeesByDepartmentTool)
registry.register(EmployeeRegisterTool)

# ── Attendance Tools ────────────────────────────────────
registry.register(AttendanceDashboardTool)
registry.register(AttendanceSummaryTool)
registry.register(AttendanceExceptionsTool)

# ── Leave Tools ─────────────────────────────────────────
registry.register(LeaveSummaryTool)
registry.register(LeaveBalanceTool)
registry.register(PendingLeavesTool)

# ── Payroll Tools ───────────────────────────────────────
registry.register(PayrollSummaryTool)
registry.register(PayrollRegisterTool)
registry.register(DepartmentSalaryCostTool)

# ── Inventory Tools ─────────────────────────────────────
registry.register(InventorySummaryTool)
registry.register(AssignedAssetsTool)
registry.register(MaintenanceHistoryTool)

# ── Payment Tools ───────────────────────────────────────
registry.register(PaymentSummaryTool)
registry.register(PendingPaymentsTool)

# ── Report Tools ────────────────────────────────────────
registry.register(HeadcountTrendTool)
registry.register(PayrollTrendTool)
registry.register(MaintenanceCostTrendTool)