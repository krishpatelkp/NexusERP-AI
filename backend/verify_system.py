import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from accounts.models import User, Role
from company.models import Company
from employees.models import Employee, Department, Designation
from leave_management.models import LeaveType, LeaveBalance
from attendance.models import Attendance
from payroll.models import PayrollCycle, Payslip
from inventory.models import Asset
from payments.models import Payment

def run_system_verification():
    print("=" * 60)
    print("NEXUSERP-AI SENIOR ARCHITECT SYSTEM AUDIT & VERIFICATION")
    print("=" * 60)
    client = Client()

    # Step 1: Clean up test tenant if exists
    test_comp_name = "Apex Dynamics Technologies"
    test_email = "founder@apexdynamics.io"
    for comp in Company.objects.filter(company_name=test_comp_name):
        Attendance.objects.filter(employee__company=comp).delete()
        LeaveBalance.objects.filter(employee__company=comp).delete()
        Employee.objects.filter(company=comp).delete()
        User.objects.filter(company=comp).delete()
        Role.objects.filter(company=comp).delete()
        Department.objects.filter(company=comp).delete()
        Designation.objects.filter(company=comp).delete()
        LeaveType.objects.filter(company=comp).delete()
        comp.delete()
    User.objects.filter(email=test_email).delete()

    # Step 2: Register new company workspace
    print("\n[TEST 1] Registering fresh company workspace...")
    reg_resp = client.post(
        "/api/auth/register/",
        data={
            "company_name": test_comp_name,
            "email": test_email,
            "username": "apexfounder",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "phone_number": "+919876543210",
        },
        content_type="application/json",
    )
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.status_code} {reg_resp.content}"
    reg_data = reg_resp.json()
    token = reg_data.get("tokens", {}).get("access") or reg_data.get("access")
    assert token, "JWT access token missing from registration response"
    print("  [PASS] Company workspace registered successfully (201 Created)")

    auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    # Step 3: Verify Founder User & Role
    print("\n[TEST 2] Verifying User Profile & Tenant Association...")
    me_resp = client.get("/api/auth/me/", **auth_headers)
    assert me_resp.status_code == 200, f"MeView failed: {me_resp.status_code} {me_resp.content}"
    me_data = me_resp.json()
    assert me_data.get("company_name") == test_comp_name, f"Wrong company: {me_data.get('company_name')}"
    assert me_data.get("role_code") == "ADMIN", f"Role is not ADMIN: {me_data.get('role_code')}"
    assert me_data.get("is_staff") is True, "Founder is not marked as staff"
    print(f"  [PASS] User is {me_data.get('email')} with role {me_data.get('role_code')} and company {me_data.get('company_name')}")

    # Step 4: Verify Bootstrap Defaults
    print("\n[TEST 3] Verifying Workspace Bootstrap Defaults...")
    company = Company.objects.get(company_name=test_comp_name)
    depts = Department.objects.filter(company=company)
    desigs = Designation.objects.filter(company=company)
    leave_types = LeaveType.objects.filter(company=company)
    assert depts.count() >= 5, f"Expected >= 5 departments, got {depts.count()}"
    assert desigs.count() >= 4, f"Expected >= 4 designations, got {desigs.count()}"
    assert leave_types.count() >= 3, f"Expected >= 3 leave types, got {leave_types.count()}"
    print(f"  [PASS] Seeded {depts.count()} departments, {desigs.count()} designations, {leave_types.count()} leave types")

    # Step 5: Verify Employees Directory (Zero Cross-Tenant Leakage)
    print("\n[TEST 4] Verifying Tenant Isolation on Employees API...")
    emp_resp = client.get("/api/employees/employees/", **auth_headers)
    assert emp_resp.status_code == 200
    emp_data = emp_resp.json()
    emp_list = emp_data if isinstance(emp_data, list) else emp_data.get("results", [])
    assert len(emp_list) == 1, f"Expected 1 founder employee, but found {len(emp_list)}! Cross-tenant leak detected!"
    founder_emp = emp_list[0]
    print(f"  [PASS] Exactly 1 employee returned: {founder_emp.get('first_name')} ({founder_emp.get('employee_id')}). Zero leak from other companies!")

    # Step 6: Verify Leave Balances
    print("\n[TEST 5] Verifying Leave Balances for Founder...")
    lb_resp = client.get("/api/leave/balances/", **auth_headers)
    assert lb_resp.status_code == 200
    lb_data = lb_resp.json()
    lb_list = lb_data if isinstance(lb_data, list) else lb_data.get("results", [])
    assert len(lb_list) >= 3, f"Expected >= 3 leave balances, got {len(lb_list)}"
    print(f"  [PASS] Initialized {len(lb_list)} leave balances for founder.")

    # Step 7: Verify Zero Payroll Leakage
    print("\n[TEST 6] Verifying Zero Cross-Tenant Payroll Leakage...")
    ps_resp = client.get("/api/payroll/my-payslips/", **auth_headers)
    assert ps_resp.status_code == 200
    ps_data = ps_resp.json()
    ps_list = ps_data if isinstance(ps_data, list) else ps_data.get("results", [])
    assert len(ps_list) == 0, f"Expected 0 payslips for fresh tenant, got {len(ps_list)}!"
    print(f"  [PASS] Exactly 0 payslips returned for fresh tenant. Clean zero state verified.")

    # Step 8: Verify Zero Inventory Leakage
    print("\n[TEST 7] Verifying Zero Cross-Tenant Inventory Leakage...")
    inv_resp = client.get("/api/inventory/assets/", **auth_headers)
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()
    inv_list = inv_data if isinstance(inv_data, list) else inv_data.get("results", [])
    assert len(inv_list) == 0, f"Expected 0 assets for fresh tenant, got {len(inv_list)}!"
    print(f"  [PASS] Exactly 0 assets returned for fresh tenant. Clean zero state verified.")

    # Step 9: Verify Zero Payment Leakage
    print("\n[TEST 8] Verifying Zero Cross-Tenant Payments Leakage...")
    pay_resp = client.get("/api/payments/", **auth_headers)
    assert pay_resp.status_code == 200
    pay_data = pay_resp.json()
    pay_list = pay_data if isinstance(pay_data, list) else pay_data.get("results", [])
    assert len(pay_list) == 0, f"Expected 0 payments for fresh tenant, got {len(pay_list)}!"
    print(f"  [PASS] Exactly 0 payments returned for fresh tenant. Clean zero state verified.")

    # Step 10: Verify Reports Summary Scoping
    print("\n[TEST 9] Verifying Scoped Reports & Analytics...")
    rep_emp = client.get("/api/reports/employees/summary/", **auth_headers)
    assert rep_emp.status_code == 200
    rep_emp_data = rep_emp.json()
    assert rep_emp_data.get("total") == 1, f"Expected total=1, got {rep_emp_data.get('total')}"
    print(f"  [PASS] Employee summary report strictly scoped: {rep_emp_data.get('total')} total employee(s).")

    # Step 11: Create a second employee & verify auto leave balances
    print("\n[TEST 10] Onboarding a new team member under this tenant...")
    eng_dept = Department.objects.filter(company=company).first()
    swe_desig = Designation.objects.filter(company=company).first()
    new_emp_resp = client.post(
        "/api/employees/employees/",
        data={
            "first_name": "Rohan",
            "last_name": "Sharma",
            "email": "rohan.sharma@apexdynamics.io",
            "phone": "+919811122233",
            "department": eng_dept.id,
            "designation": swe_desig.id,
            "employment_type": "Full-Time",
            "gender": "Male",
            "marital_status": "Single",
            "date_of_birth": "1995-05-15",
            "joining_date": "2026-01-10",
            "blood_group": "B+",
            "pan_number": "ABCDE1234F",
            "aadhar_number": "123456789012",
            "basic_salary": "65000.00",
        },
        content_type="application/json",
        **auth_headers,
    )
    assert new_emp_resp.status_code in (200, 201), f"Employee creation failed: {new_emp_resp.status_code} {new_emp_resp.content}"
    created_emp = new_emp_resp.json()
    created_emp_id = created_emp.get("id")
    print(f"  [PASS] Created new employee: {created_emp.get('first_name')} {created_emp.get('last_name')} (ID: {created_emp_id})")

    # Verify that new employee automatically received leave balances
    new_emp_obj = Employee.objects.get(id=created_emp_id)
    new_balances = LeaveBalance.objects.filter(employee=new_emp_obj)
    assert new_balances.count() >= 3, f"Expected auto-initialized leave balances, got {new_balances.count()}"
    print(f"  [PASS] New employee automatically initialized with {new_balances.count()} active leave balance records.")

    # Step 12: Verify Attendance Check-In / Check-Out
    print("\n[TEST 11] Testing Attendance Check-In / Check-Out workflow...")
    checkin_resp = client.post(
        "/api/attendance/check-in/",
        data={"employee": created_emp_id},
        content_type="application/json",
        **auth_headers,
    )
    assert checkin_resp.status_code in (200, 201), f"Check-in failed: {checkin_resp.status_code} {checkin_resp.content}"
    print("  [PASS] Check-in recorded successfully.")

    checkout_resp = client.post(
        "/api/attendance/check-out/",
        data={"employee": created_emp_id},
        content_type="application/json",
        **auth_headers,
    )
    assert checkout_resp.status_code == 200, f"Check-out failed: {checkout_resp.status_code} {checkout_resp.content}"
    print("  [PASS] Check-out recorded successfully.")

    # Step 13: Verify Profile Update & Password Change
    print("\n[TEST 12] Testing Profile Update & Security API...")
    update_prof = client.patch(
        "/api/auth/me/update/",
        data={"username": "apexfounder_updated", "phone_number": "+919999888877"},
        content_type="application/json",
        **auth_headers,
    )
    assert update_prof.status_code == 200, f"Profile update failed: {update_prof.status_code} {update_prof.content}"
    assert update_prof.json().get("user", {}).get("username") == "apexfounder_updated"
    print("  [PASS] Profile username and phone successfully updated.")

    pw_resp = client.post(
        "/api/auth/change-password/",
        data={
            "old_password": "Password123!",
            "new_password": "NewSecurePassword456!",
            "confirm_password": "NewSecurePassword456!",
        },
        content_type="application/json",
        **auth_headers,
    )
    assert pw_resp.status_code == 200, f"Change password failed: {pw_resp.status_code} {pw_resp.content}"
    print("  [PASS] Password changed successfully.")

    print("\n" + "=" * 60)
    print("ALL 12 ENTERPRISE VERIFICATION SUITES PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_system_verification()
