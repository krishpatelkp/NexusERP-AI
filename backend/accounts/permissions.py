from rest_framework.permissions import BasePermission


# ─────────────────────────────────────────
# BASE PERMISSION CLASS
# ─────────────────────────────────────────

class HasPermission(BasePermission):
    """
    Base class for all NexusERP permission classes.

    Child classes only need to define
    the permission_code attribute.
    """

    permission_code = None

    def has_permission(self, request, view):
        """
        Check whether the authenticated user
        has the required business permission.
        """

        if self.permission_code is None:
            return False

        if not request.user.is_authenticated:
            return False

        return request.user.has_perm_code(
            self.permission_code
        )


# ─────────────────────────────────────────
# COMPANY PERMISSIONS
# ─────────────────────────────────────────

class HasCompanyViewPermission(HasPermission):
    """Allows viewing company information."""
    permission_code = "company.view"


class HasCompanyUpdatePermission(HasPermission):
    """Allows updating company information."""
    permission_code = "company.update"


class HasCompanySettingsPermission(HasPermission):
    """Allows managing company settings."""
    permission_code = "company.settings"


# ─────────────────────────────────────────
# EMPLOYEE PERMISSIONS
# ─────────────────────────────────────────

class HasEmployeeCreatePermission(HasPermission):
    """Allows creating employees."""
    permission_code = "employee.create"


class HasEmployeeViewPermission(HasPermission):
    """Allows viewing employees."""
    permission_code = "employee.view"


class HasEmployeeUpdatePermission(HasPermission):
    """Allows updating employees."""
    permission_code = "employee.update"


class HasEmployeeDeletePermission(HasPermission):
    """Allows deleting employees."""
    permission_code = "employee.delete"


class HasEmployeeImportPermission(HasPermission):
    """Allows importing employees."""
    permission_code = "employee.import"


class HasEmployeeExportPermission(HasPermission):
    """Allows exporting employees."""
    permission_code = "employee.export"


# ─────────────────────────────────────────
# ATTENDANCE PERMISSIONS
# ─────────────────────────────────────────

class HasAttendanceMarkPermission(HasPermission):
    """Allows marking attendance."""
    permission_code = "attendance.mark"


class HasAttendanceViewPermission(HasPermission):
    """Allows viewing attendance."""
    permission_code = "attendance.view"


class HasAttendanceUpdatePermission(HasPermission):
    """Allows updating attendance."""
    permission_code = "attendance.update"


class HasAttendanceApprovePermission(HasPermission):
    """Allows approving attendance."""
    permission_code = "attendance.approve"


class HasAttendanceExportPermission(HasPermission):
    """Allows exporting attendance."""
    permission_code = "attendance.export"


# ─────────────────────────────────────────
# LEAVE PERMISSIONS
# ─────────────────────────────────────────

class HasLeaveCreatePermission(HasPermission):
    """Allows creating leave requests."""
    permission_code = "leave.create"


class HasLeaveViewPermission(HasPermission):
    """Allows viewing leave requests."""
    permission_code = "leave.view"


class HasLeaveUpdatePermission(HasPermission):
    """Allows updating leave requests."""
    permission_code = "leave.update"


class HasLeaveApprovePermission(HasPermission):
    """Allows approving leave requests."""
    permission_code = "leave.approve"


class HasLeaveRejectPermission(HasPermission):
    """Allows rejecting leave requests."""
    permission_code = "leave.reject"


class HasLeaveCancelPermission(HasPermission):
    """Allows cancelling leave requests."""
    permission_code = "leave.cancel"


# ─────────────────────────────────────────
# PAYROLL PERMISSIONS
# ─────────────────────────────────────────

class HasPayrollGeneratePermission(HasPermission):
    """Allows generating payroll."""
    permission_code = "payroll.generate"


class HasPayrollViewPermission(HasPermission):
    """Allows viewing payroll."""
    permission_code = "payroll.view"


class HasPayrollUpdatePermission(HasPermission):
    """Allows updating payroll."""
    permission_code = "payroll.update"


class HasPayrollApprovePermission(HasPermission):
    """Allows approving payroll."""
    permission_code = "payroll.approve"


class HasPayrollExportPermission(HasPermission):
    """Allows exporting payroll."""
    permission_code = "payroll.export"


# ─────────────────────────────────────────
# INVENTORY PERMISSIONS
# ─────────────────────────────────────────

class HasInventoryCreatePermission(HasPermission):
    """Allows creating inventory."""
    permission_code = "inventory.create"


class HasInventoryViewPermission(HasPermission):
    """Allows viewing inventory."""
    permission_code = "inventory.view"


class HasInventoryUpdatePermission(HasPermission):
    """Allows updating inventory."""
    permission_code = "inventory.update"


class HasInventoryDeletePermission(HasPermission):
    """Allows deleting inventory."""
    permission_code = "inventory.delete"


class HasInventoryExportPermission(HasPermission):
    """Allows exporting inventory."""
    permission_code = "inventory.export"


# ─────────────────────────────────────────
# REPORTS PERMISSIONS
# ─────────────────────────────────────────

class HasReportsViewPermission(HasPermission):
    """Allows viewing reports."""
    permission_code = "reports.view"


class HasReportsExportPermission(HasPermission):
    """Allows exporting reports."""
    permission_code = "reports.export"


class HasReportsSchedulePermission(HasPermission):
    """Allows scheduling reports."""
    permission_code = "reports.schedule"


# ─────────────────────────────────────────
# NOTIFICATION PERMISSIONS
# ─────────────────────────────────────────

class HasNotificationsViewPermission(HasPermission):
    """Allows viewing notifications."""
    permission_code = "notifications.view"


class HasNotificationsSendPermission(HasPermission):
    """Allows sending notifications."""
    permission_code = "notifications.send"


class HasNotificationsManagePermission(HasPermission):
    """Allows managing notifications."""
    permission_code = "notifications.manage"


# ─────────────────────────────────────────
# AI PERMISSIONS
# ─────────────────────────────────────────

class HasAIChatPermission(HasPermission):
    """Allows using the AI Business Copilot."""
    permission_code = "ai.chat"


class HasAIAnalyticsPermission(HasPermission):
    """Allows running AI analytics."""
    permission_code = "ai.analytics"


class HasAIPredictionsPermission(HasPermission):
    """Allows running AI predictions."""
    permission_code = "ai.predictions"


class HasAIOCRPermission(HasPermission):
    """Allows using AI OCR."""
    permission_code = "ai.ocr"


class HasAIReportsPermission(HasPermission):
    """Allows generating AI reports."""
    permission_code = "ai.reports"


# ─────────────────────────────────────────
# SETTINGS PERMISSIONS
# ─────────────────────────────────────────

class HasSettingsViewPermission(HasPermission):
    """Allows viewing system settings."""
    permission_code = "settings.view"


class HasSettingsUpdatePermission(HasPermission):
    """Allows updating system settings."""
    permission_code = "settings.update"


class HasSettingsPermissionsPermission(HasPermission):
    """Allows managing role permissions."""
    permission_code = "settings.permissions"


class HasSettingsAuditPermission(HasPermission):
    """Allows viewing audit logs."""
    permission_code = "settings.audit"


# ─────────────────────────────────────────
# DEPARTMENT PERMISSIONS
# ─────────────────────────────────────────

class HasDepartmentCreatePermission(HasPermission):
    """Allows user to create departments."""
    permission_code = "department.create"


class HasDepartmentViewPermission(HasPermission):
    """Allows user to view departments."""
    permission_code = "department.view"


class HasDepartmentUpdatePermission(HasPermission):
    """Allows user to update departments."""
    permission_code = "department.update"


class HasDepartmentDeletePermission(HasPermission):
    """Allows user to delete departments."""
    permission_code = "department.delete"


class HasDesignationCreatePermission(HasPermission):
    permission_code = "designation.create"


class HasDesignationViewPermission(HasPermission):
    permission_code = "designation.view"


class HasDesignationUpdatePermission(HasPermission):
    permission_code = "designation.update"


class HasDesignationDeletePermission(HasPermission):
    permission_code = "designation.delete"


# ==========================================================
# EMPLOYEE ADDRESS PERMISSIONS
# ==========================================================

class HasEmployeeAddressCreatePermission(
    HasPermission,
):
    """
    Allows creating employee addresses.
    """
    permission_code = (
        "employee_address.create"
    )


class HasEmployeeAddressViewPermission(
    HasPermission,
):
    """
    Allows viewing employee addresses.
    """
    permission_code = (
        "employee_address.view"
    )


class HasEmployeeAddressUpdatePermission(
    HasPermission,
):
    """
    Allows updating employee addresses.
    """
    permission_code = (
        "employee_address.update"
    )


class HasEmployeeAddressDeletePermission(
    HasPermission,
):
    """
    Allows deleting employee addresses.
    """
    permission_code = (
        "employee_address.delete"
    )


# ==========================================================
# EMERGENCY CONTACT PERMISSIONS
# ==========================================================

class HasEmergencyContactCreatePermission(
    HasPermission,
):
    """Allows creating emergency contacts."""
    permission_code = "emergency_contact.create"


class HasEmergencyContactViewPermission(
    HasPermission,
):
    """Allows viewing emergency contacts."""
    permission_code = "emergency_contact.view"


class HasEmergencyContactUpdatePermission(
    HasPermission,
):
    """Allows updating emergency contacts."""
    permission_code = "emergency_contact.update"


class HasEmergencyContactDeletePermission(
    HasPermission,
):
    """Allows deleting emergency contacts."""
    permission_code = "emergency_contact.delete"