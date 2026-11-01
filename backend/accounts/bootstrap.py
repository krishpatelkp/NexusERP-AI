"""
Workspace Bootstrapper for NexusERP-AI
Creates isolated default configuration, roles, permissions, departments,
designations, shift, leave types, asset categories, and founder employee profile
for newly registered company workspaces.
"""
import uuid
from datetime import date
from django.utils import timezone
from django.db import transaction

from accounts.models import Role, Permission, RolePermission
from company.models import Company
from employees.models import Department, Designation, Shift, Employee
from leave_management.models import LeaveType, LeaveBalance
from inventory.models import AssetCategory


@transaction.atomic
def bootstrap_workspace(company: Company, user=None):
    """
    Sets up a complete, isolated workspace environment for a new company.
    """
    if not company:
        return None

    # 1. Admin Role & Full Permissions
    admin_role = Role.objects.filter(company=company, role_code="ADMIN").first()
    if not admin_role:
        admin_role = Role.objects.create(
            company=company,
            role_name="Admin",
            role_code="ADMIN",
            description="Company Owner & System Administrator",
            is_active=True,
        )

    # Attach all active business permissions to the Admin role
    active_perms = Permission.objects.filter(is_active=True)
    for perm in active_perms:
        RolePermission.objects.get_or_create(
            role=admin_role,
            permission=perm,
            defaults={"is_active": True},
        )

    # 2. Default Departments
    default_departments = [
        ("Engineering", "ENG", "Technical Architecture, Software Development & Infrastructure"),
        ("Human Resources", "HR", "People Operations, Talent Acquisition & Workforce Care"),
        ("Finance & Accounts", "FIN", "Corporate Accounting, Payroll & Financial Compliance"),
        ("Operations", "OPS", "Business Operations, Facilities & Equipment Logistics"),
        ("Sales & Marketing", "SAL", "Client Success, Growth & Corporate Revenue"),
    ]
    created_depts = {}
    for name, code, desc in default_departments:
        dept, _ = Department.objects.get_or_create(
            company=company,
            department_code=code,
            defaults={
                "department_name": name,
                "description": desc,
                "is_active": True,
            },
        )
        created_depts[code] = dept

    # 3. Default Designations
    default_designations = [
        ("Director & Founder", "DIR", "Executive Leadership & Corporate Direction"),
        ("Senior Software Engineer", "SWE", "Full-Stack Development & Architecture"),
        ("HR Operations Lead", "HRS", "People Operations & HR Administration"),
        ("Financial Analyst", "FA", "Corporate Accounts & Payroll Auditing"),
    ]
    created_desigs = {}
    for name, code, desc in default_designations:
        desig, _ = Designation.objects.get_or_create(
            company=company,
            designation_code=code,
            defaults={
                "designation_name": name,
                "description": desc,
                "is_active": True,
            },
        )
        created_desigs[code] = desig

    # 4. Default Shift (General Shift 09:00 - 18:00)
    default_shift = Shift.objects.filter(company=company, is_default=True).first()
    if not default_shift:
        default_shift = Shift.objects.filter(company=company, shift_code="GEN").first()
    if not default_shift:
        default_shift = Shift.objects.create(
            company=company,
            shift_name="General Day Shift",
            shift_code="GEN",
            start_time="09:00:00",
            end_time="18:00:00",
            grace_minutes=15,
            is_default=True,
            is_active=True,
        )

    # 5. Default Leave Types
    default_leave_types = [
        ("Casual Leave", "CL", "Standard paid casual leave days", 12),
        ("Sick Leave", "SL", "Medical and health-related leave", 10),
        ("Paid Time Off", "PTO", "Annual paid vacation and personal leave", 15),
    ]
    created_leave_types = []
    for name, code, desc, max_days in default_leave_types:
        lt, _ = LeaveType.objects.get_or_create(
            company=company,
            leave_code=code,
            defaults={
                "leave_name": name,
                "description": desc,
                "max_days_per_year": max_days,
                "max_consecutive_days": min(max_days, 5),
                "is_paid": True,
                "is_active": True,
            },
        )
        created_leave_types.append(lt)

    # 6. Default Asset Categories
    default_asset_categories = [
        ("Laptops & Workstations", "Portable computers, developer laptops and towers"),
        ("Monitors & Displays", "External 4K displays and workstation monitors"),
        ("Mobile Devices", "Company smartphones and testing tablets"),
        ("Office Infrastructure", "Desks, ergonomic chairs and facility equipment"),
    ]
    for cat_name, cat_desc in default_asset_categories:
        AssetCategory.objects.get_or_create(
            company=company,
            name=cat_name,
            defaults={
                "description": cat_desc,
                "is_active": True,
            },
        )

    # 7. Founder Employee Profile
    if user:
        # Assign role and company
        user.company = company
        user.role = admin_role
        user.is_staff = True
        user.save(update_fields=["company", "role", "is_staff"])

        # Check if an Employee profile already exists
        emp = getattr(user, "employee_profile", None)
        if not emp:
            emp = Employee.objects.filter(company=company, email=user.email).first()

        if not emp:
            emp_code = f"EMP-{uuid.uuid4().hex[:4].upper()}"
            eng_dept = created_depts.get("ENG")
            founder_desig = created_desigs.get("DIR")

            emp = Employee.objects.create(
                employee_id=emp_code,
                first_name=user.username or "Admin",
                last_name="Executive",
                gender="Male",
                marital_status="Single",
                blood_group="O+",
                date_of_birth=date(1995, 1, 1),
                email=user.email,
                phone=user.phone_number or "+919876543210",
                company=company,
                department=eng_dept,
                designation=founder_desig,
                user_account=user,
                employment_type="Full-Time",
                joining_date=timezone.localdate(),
                basic_salary=100000.00,
                employee_status="Active",
                is_active=True,
            )

        # 8. Initialize Leave Balances for Founder Employee
        current_year = timezone.localdate().year
        for lt in created_leave_types:
            LeaveBalance.objects.get_or_create(
                company=company,
                employee=emp,
                leave_type=lt,
                year=current_year,
                defaults={
                    "allocated_days": lt.max_days_per_year,
                    "remaining_days": lt.max_days_per_year,
                    "used_days": 0,
                },
            )

    return company
