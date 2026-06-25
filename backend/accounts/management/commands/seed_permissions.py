from django.core.management.base import BaseCommand

from accounts.models import Permission


# ─────────────────────────────────────────
# COMPLETE PERMISSION CATALOG
# ─────────────────────────────────────────

PERMISSIONS = [

    # Company
    {
        "permission_name": "View Company",
        "permission_code": "company.view",
        "description": "View company information",
    },
    {
        "permission_name": "Update Company",
        "permission_code": "company.update",
        "description": "Update company information",
    },
    {
        "permission_name": "Company Settings",
        "permission_code": "company.settings",
        "description": "Manage company settings",
    },

    # Employee
    {
        "permission_name": "Create Employee",
        "permission_code": "employee.create",
        "description": "Create new employee records",
    },
    {
        "permission_name": "View Employee",
        "permission_code": "employee.view",
        "description": "View employee records",
    },
    {
        "permission_name": "Update Employee",
        "permission_code": "employee.update",
        "description": "Update employee records",
    },
    {
        "permission_name": "Delete Employee",
        "permission_code": "employee.delete",
        "description": "Delete employee records",
    },
    {
        "permission_name": "Import Employees",
        "permission_code": "employee.import",
        "description": "Import employees from file",
    },
    {
        "permission_name": "Export Employees",
        "permission_code": "employee.export",
        "description": "Export employee data",
    },

    # Attendance
    {
        "permission_name": "Mark Attendance",
        "permission_code": "attendance.mark",
        "description": "Mark employee attendance",
    },
    {
        "permission_name": "View Attendance",
        "permission_code": "attendance.view",
        "description": "View attendance records",
    },
    {
        "permission_name": "Update Attendance",
        "permission_code": "attendance.update",
        "description": "Update attendance records",
    },
    {
        "permission_name": "Approve Attendance",
        "permission_code": "attendance.approve",
        "description": "Approve attendance entries",
    },
    {
        "permission_name": "Export Attendance",
        "permission_code": "attendance.export",
        "description": "Export attendance data",
    },

    # Leave
    {
        "permission_name": "Create Leave",
        "permission_code": "leave.create",
        "description": "Apply for leave",
    },
    {
        "permission_name": "View Leave",
        "permission_code": "leave.view",
        "description": "View leave records",
    },
    {
        "permission_name": "Update Leave",
        "permission_code": "leave.update",
        "description": "Update leave requests",
    },
    {
        "permission_name": "Approve Leave",
        "permission_code": "leave.approve",
        "description": "Approve leave requests",
    },
    {
        "permission_name": "Reject Leave",
        "permission_code": "leave.reject",
        "description": "Reject leave requests",
    },
    {
        "permission_name": "Cancel Leave",
        "permission_code": "leave.cancel",
        "description": "Cancel leave requests",
    },

    # Payroll
    {
        "permission_name": "Generate Payroll",
        "permission_code": "payroll.generate",
        "description": "Generate payroll",
    },
    {
        "permission_name": "View Payroll",
        "permission_code": "payroll.view",
        "description": "View payroll records",
    },
    {
        "permission_name": "Update Payroll",
        "permission_code": "payroll.update",
        "description": "Update payroll",
    },
    {
        "permission_name": "Approve Payroll",
        "permission_code": "payroll.approve",
        "description": "Approve payroll",
    },
    {
        "permission_name": "Export Payroll",
        "permission_code": "payroll.export",
        "description": "Export payroll data",
    },

    # Inventory
    {
        "permission_name": "Create Inventory",
        "permission_code": "inventory.create",
        "description": "Create inventory items",
    },
    {
        "permission_name": "View Inventory",
        "permission_code": "inventory.view",
        "description": "View inventory records",
    },
    {
        "permission_name": "Update Inventory",
        "permission_code": "inventory.update",
        "description": "Update inventory records",
    },
    {
        "permission_name": "Delete Inventory",
        "permission_code": "inventory.delete",
        "description": "Delete inventory items",
    },
    {
        "permission_name": "Export Inventory",
        "permission_code": "inventory.export",
        "description": "Export inventory data",
    },

    # Reports
    {
        "permission_name": "View Reports",
        "permission_code": "reports.view",
        "description": "View reports",
    },
    {
        "permission_name": "Export Reports",
        "permission_code": "reports.export",
        "description": "Export reports",
    },
    {
        "permission_name": "Schedule Reports",
        "permission_code": "reports.schedule",
        "description": "Schedule reports",
    },

    # Notifications
    {
        "permission_name": "View Notifications",
        "permission_code": "notifications.view",
        "description": "View notifications",
    },
    {
        "permission_name": "Send Notifications",
        "permission_code": "notifications.send",
        "description": "Send notifications",
    },
    {
        "permission_name": "Manage Notifications",
        "permission_code": "notifications.manage",
        "description": "Manage notifications",
    },

    # AI
    {
        "permission_name": "AI Chat",
        "permission_code": "ai.chat",
        "description": "Access AI Business Copilot",
    },
    {
        "permission_name": "AI Analytics",
        "permission_code": "ai.analytics",
        "description": "Run AI analytics",
    },
    {
        "permission_name": "AI Predictions",
        "permission_code": "ai.predictions",
        "description": "Access AI predictions",
    },
    {
        "permission_name": "AI OCR",
        "permission_code": "ai.ocr",
        "description": "Process invoices using OCR",
    },
    {
        "permission_name": "AI Reports",
        "permission_code": "ai.reports",
        "description": "Generate AI reports",
    },

    # Settings
    {
        "permission_name": "View Settings",
        "permission_code": "settings.view",
        "description": "View system settings",
    },
    {
        "permission_name": "Update Settings",
        "permission_code": "settings.update",
        "description": "Update system settings",
    },
    {
        "permission_name": "Manage Permissions",
        "permission_code": "settings.permissions",
        "description": "Manage role permissions",
    },
    {
        "permission_name": "View Audit Log",
        "permission_code": "settings.audit",
        "description": "View system audit log",
    },
    # Department
    {
        "permission_name": "Create Department",
        "permission_code": "department.create",
        "description": "Create new departments",
    },
    {
        "permission_name": "View Department",
        "permission_code": "department.view",
        "description": "View departments",
    },
    {
        "permission_name": "Update Department",
        "permission_code": "department.update",
        "description": "Update departments",
    },
    {
        "permission_name": "Delete Department",
        "permission_code": "department.delete",
        "description": "Delete departments",
    },
    # Designation
    {
        "permission_name": "Create Designation",
        "permission_code": "designation.create",
        "description": "Create new designations",
    },
    {
        "permission_name": "View Designation",
        "permission_code": "designation.view",
        "description": "View designations",
    },
    {
        "permission_name": "Update Designation",
        "permission_code": "designation.update",
        "description": "Update designations",
    },
    {
        "permission_name": "Delete Designation",
        "permission_code": "designation.delete",
        "description": "Delete designations",
    },
]


class Command(BaseCommand):

    help = (
        "Create or update all NexusERP "
        "business permissions."
    )

    def handle(self, *args, **kwargs):

        created_count = 0
        updated_count = 0

        for permission in PERMISSIONS:

            _, created = Permission.objects.update_or_create(
                permission_code=permission["permission_code"],
                defaults={
                    "permission_name": permission["permission_name"],
                    "description": permission["description"],
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created : {permission['permission_code']}"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated : {permission['permission_code']}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done! {created_count} created, {updated_count} updated."
            )
        )