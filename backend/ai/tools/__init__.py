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

# Register all employee tools
registry.register(EmployeeSummaryTool)
registry.register(EmployeesByDepartmentTool)
registry.register(EmployeeRegisterTool)

# Attendance, Leave, Payroll, Inventory, Payment tools
# will be registered here as they are built.