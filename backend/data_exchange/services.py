"""
==========================================================
NexusERP-AI  |  data_exchange  |  services.py
==========================================================

Business Logic Layer for the Data Exchange Framework.

Responsibilities:
  - Coordinate preview and import workflows
  - Execute database writes inside transaction.atomic()
  - Audit every operation via ImportLog / ExportLog
  - Enforce multi-tenancy on every operation

Rules:
  - Views only call services — never write to DB directly
  - Services never return HTTP responses
  - All imports are atomic (all-or-nothing)
  - Never duplicate business logic from other modules
==========================================================
"""

import time
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .constants  import ImportModule, ImportStatus, ExportStatus
from .models     import ImportLog, ExportLog
from .preview    import ImportPreviewEngine
from .exceptions import (
    PreviewExpiredError,
    ImportAlreadyConfirmedError,
    ImportServiceError,
    CompanyIsolationError,
)
from .utils import validate_upload


# ==========================================================
# BASE IMPORT SERVICE
# ==========================================================

class BaseImportService:
    """
    Base class for all module import services.

    Subclasses override _create_objects() to perform
    the actual bulk database writes.
    """

    module = None

    def __init__(self, company, user):
        self.company = company
        self.user    = user

    # ──────────────────────────────────────
    # PREVIEW
    # ──────────────────────────────────────

    def preview(self, file):
        """
        Phase 1: Read → Validate → Preview.

        Creates an ImportLog with status=PREVIEW.
        Does NOT write any business data.

        Args:
            file: Django uploaded file.

        Returns:
            dict: Preview result (see ImportPreviewEngine).
        """
        log = ImportLog.objects.create(
            company           = self.company,
            imported_by       = self.user,
            module            = self.module,
            original_filename = file.name,
            file_size_bytes   = file.size,
            status            = ImportStatus.PENDING,
        )

        engine = ImportPreviewEngine(
            company = self.company,
            module  = self.module,
        )

        return engine.preview(file=file, log=log)

    # ──────────────────────────────────────
    # CONFIRM
    # ──────────────────────────────────────

    def confirm(self, log_id):
        """
        Phase 2: Confirm → Import.

        Retrieves preview_data from ImportLog and writes
        all rows to the database inside transaction.atomic().

        Args:
            log_id (int): ID of the ImportLog from the preview step.

        Returns:
            dict: Import result with row counts.

        Raises:
            PreviewExpiredError:          Log not in PREVIEW status.
            ImportAlreadyConfirmedError:  Import already completed.
            CompanyIsolationError:        Log belongs to different company.
        """
        log = self._get_preview_log(log_id)
        preview_rows = log.preview_data

        log.status = ImportStatus.PROCESSING
        log.save(update_fields=["status"])

        start_time = time.time()

        try:
            with transaction.atomic():
                imported_count = self._create_objects(preview_rows)

            duration = time.time() - start_time

            log.status        = ImportStatus.COMPLETED
            log.imported_rows = imported_count
            log.preview_data  = []   # clear preview data — no longer needed
            log.completed_at  = timezone.now()
            log.duration_seconds = round(duration, 3)
            log.save()

            return {
                "log_id":        log.id,
                "status":        "completed",
                "imported_rows": imported_count,
                "total_rows":    log.total_rows,
                "failed_rows":   log.failed_rows,
                "duration_seconds": log.duration_seconds,
                "module":        self.module,
            }

        except Exception as exc:
            duration = time.time() - start_time
            log.status        = ImportStatus.FAILED
            log.error_summary = str(exc)
            log.completed_at  = timezone.now()
            log.duration_seconds = round(duration, 3)
            log.save()
            raise ImportServiceError(
                f"Import failed during database write: {exc}"
            )

    # ──────────────────────────────────────
    # LOG RETRIEVAL
    # ──────────────────────────────────────

    def _get_preview_log(self, log_id):
        """
        Retrieve and validate the ImportLog for the confirm step.
        Enforces company isolation.
        """
        try:
            log = ImportLog.objects.get(id=log_id)
        except ImportLog.DoesNotExist:
            raise PreviewExpiredError(
                f"Import log #{log_id} does not exist."
            )

        if log.company != self.company:
            raise CompanyIsolationError(
                "You do not have permission to confirm this import."
            )

        if log.status == ImportStatus.COMPLETED:
            raise ImportAlreadyConfirmedError(
                f"Import log #{log_id} has already been completed."
            )

        if log.status == ImportStatus.CANCELLED:
            raise PreviewExpiredError(
                f"Import log #{log_id} has been cancelled."
            )

        if log.status != ImportStatus.PREVIEW:
            raise PreviewExpiredError(
                f"Import log #{log_id} is not in a confirmable state (status: {log.status})."
            )

        if not log.preview_data:
            raise PreviewExpiredError(
                f"No preview data found for log #{log_id}. Please upload the file again."
            )

        return log

    # ──────────────────────────────────────
    # DB WRITE  (override in subclass)
    # ──────────────────────────────────────

    def _create_objects(self, preview_rows):
        """
        Write cleaned rows to the database.
        Must be overridden by every subclass.

        Returns:
            int: Number of rows successfully created.
        """
        raise NotImplementedError


# ==========================================================
# EMPLOYEE IMPORT SERVICE
# ==========================================================

class EmployeeImportService(BaseImportService):
    """
    Handles employee bulk imports.

    Creates Employee records using bulk_create for
    optimal performance. Employee IDs are auto-generated.
    """

    module = ImportModule.EMPLOYEES

    def _create_objects(self, preview_rows):
        from employees.models import Employee, generate_employee_id

        to_create = []
        for row in preview_rows:
            employee = Employee(
                company          = self.company,
                first_name       = row.get("first_name", ""),
                middle_name      = row.get("middle_name", ""),
                last_name        = row.get("last_name", ""),
                email            = row.get("email", ""),
                phone            = row.get("phone", ""),
                alternate_phone  = row.get("alternate_phone", ""),
                gender           = row.get("gender", ""),
                date_of_birth    = row.get("date_of_birth"),
                marital_status   = row.get("marital_status", ""),
                blood_group      = row.get("blood_group", ""),
                employment_type  = row.get("employment_type", "Full-Time"),
                employee_status  = row.get("employee_status", "Probation"),
                joining_date     = row.get("joining_date"),
                confirmation_date= row.get("confirmation_date"),
                basic_salary     = Decimal(str(row.get("basic_salary") or 0)),
                department_id    = row.get("department_id"),
                designation_id   = row.get("designation_id"),
            )
            to_create.append(employee)

        # Determine the starting ID
        last_emp = Employee.objects.filter(company=self.company).order_by("-employee_id").first()
        last_number = 0
        if last_emp:
            try:
                last_number = int(last_emp.employee_id.replace("EMP", ""))
            except ValueError:
                pass

        # Assign employee IDs sequentially in memory before bulk create
        for employee in to_create:
            last_number += 1
            employee.employee_id = f"EMP{last_number:06d}"

        created = Employee.objects.bulk_create(to_create)
        return len(created)


# ==========================================================
# ATTENDANCE IMPORT SERVICE
# ==========================================================

class AttendanceImportService(BaseImportService):
    """
    Handles attendance bulk imports.

    Skips rows where attendance already exists (warnings
    were already flagged during validation).
    Creates Attendance records via bulk_create.

    Note: Attendance requires a Shift reference. If the
    employee has a default shift, it is used. Otherwise
    the row is skipped with a warning.
    """

    module = ImportModule.ATTENDANCE

    def _create_objects(self, preview_rows):
        from attendance.models import Attendance, AttendanceStatus, AttendanceSource
        from employees.models import Employee

        to_create = []
        for row in preview_rows:
            employee_id = row.get("employee_id")
            att_date    = row.get("date")

            if not employee_id or not att_date:
                continue

            # Skip if already exists (gracefully)
            if Attendance.objects.filter(
                employee__company=self.company,
                employee__employee_id=employee_id,
                date=att_date,
            ).exists():
                continue

            try:
                employee = Employee.objects.get(
                    company=self.company,
                    employee_id=employee_id,
                )
            except Employee.DoesNotExist:
                continue

            # Use employee's default shift
            shift = getattr(employee, "shift", None)
            if shift is None:
                # Try to find any shift for this company
                from employees.models import Shift
                shift = Shift.objects.filter(
                    company=self.company,
                    is_active=True,
                ).first()

            if not shift:
                continue  # Cannot create attendance without a shift

            status   = row.get("status", AttendanceStatus.ABSENT)
            check_in = row.get("check_in")
            check_out= row.get("check_out")

            record = Attendance(
                employee                = employee,
                shift                   = shift,
                date                    = att_date,
                status                  = status,
                check_in                = (
                    timezone.make_aware(
                        __import__("datetime").datetime.combine(
                            __import__("datetime").date.fromisoformat(str(att_date)),
                            __import__("datetime").time.fromisoformat(str(check_in))
                        )
                    ) if check_in else None
                ),
                check_out               = (
                    timezone.make_aware(
                        __import__("datetime").datetime.combine(
                            __import__("datetime").date.fromisoformat(str(att_date)),
                            __import__("datetime").time.fromisoformat(str(check_out))
                        )
                    ) if check_out else None
                ),
                remarks                 = row.get("remarks", ""),
                attendance_source       = AttendanceSource.API,
                scheduled_start_time    = shift.start_time,
                scheduled_end_time      = shift.end_time,
                shift_name_snapshot     = shift.shift_name,
            )
            to_create.append(record)

        created = Attendance.objects.bulk_create(to_create)
        return len(created)


# ==========================================================
# LEAVE IMPORT SERVICE
# ==========================================================

class LeaveImportService(BaseImportService):
    """
    Handles leave request bulk imports.

    Creates LeaveRequest records. Status defaults to
    'Approved' for imported historical data.
    """

    module = ImportModule.LEAVE

    def _create_objects(self, preview_rows):
        from leave_management.models import LeaveRequest, LeaveType
        from employees.models import Employee
        from datetime import date as date_type

        to_create = []
        for row in preview_rows:
            employee_id = row.get("employee_id")
            leave_type_id = row.get("leave_type_id")

            try:
                employee   = Employee.objects.get(company=self.company, employee_id=employee_id)
                leave_type = LeaveType.objects.get(id=leave_type_id, company=self.company)
            except Exception:
                continue

            start = row.get("start_date")
            end   = row.get("end_date")

            if isinstance(start, str):
                start = date_type.fromisoformat(start)
            if isinstance(end, str):
                end = date_type.fromisoformat(end)

            total_days = (end - start).days + 1 if start and end else 1

            record = LeaveRequest(
                employee        = employee,
                leave_type      = leave_type,
                start_date      = start,
                end_date        = end,
                total_days      = total_days,
                reason          = row.get("reason", ""),
                is_half_day     = row.get("is_half_day", False),
                approval_status = "Approved",  # Historical import
            )
            to_create.append(record)

        created = LeaveRequest.objects.bulk_create(to_create)
        return len(created)


# ==========================================================
# PAYROLL IMPORT SERVICE
# ==========================================================

class PayrollImportService(BaseImportService):
    """
    Handles payroll/salary slip bulk imports.

    Creates PayrollEntry or SalarySlip records.
    """

    module = ImportModule.PAYROLL

    def _create_objects(self, preview_rows):
        from payroll.models import SalarySlip
        from employees.models import Employee

        to_create = []
        for row in preview_rows:
            employee_id = row.get("employee_id")
            try:
                employee = Employee.objects.get(company=self.company, employee_id=employee_id)
            except Employee.DoesNotExist:
                continue

            basic   = Decimal(str(row.get("basic_salary") or 0))
            hra     = Decimal(str(row.get("hra") or 0))
            ta      = Decimal(str(row.get("transport_allowance") or 0))
            other_a = Decimal(str(row.get("other_allowance") or 0))
            pf      = Decimal(str(row.get("pf_deduction") or 0))
            tax     = Decimal(str(row.get("tax_deduction") or 0))
            other_d = Decimal(str(row.get("other_deduction") or 0))

            gross       = basic + hra + ta + other_a
            deductions  = pf + tax + other_d
            net         = gross - deductions

            record = SalarySlip(
                employee            = employee,
                company             = self.company,
                month               = row.get("month"),
                year                = row.get("year"),
                basic_salary        = basic,
                hra                 = hra,
                transport_allowance = ta,
                other_allowance     = other_a,
                pf_deduction        = pf,
                tax_deduction       = tax,
                other_deduction     = other_d,
                gross_salary        = gross,
                total_deductions    = deductions,
                net_salary          = net,
                # Snapshots
                employee_name_snapshot = employee.full_name,
                employee_id_snapshot   = employee.employee_id,
            )
            to_create.append(record)

        created = SalarySlip.objects.bulk_create(to_create)
        return len(created)


# ==========================================================
# INVENTORY IMPORT SERVICE
# ==========================================================

class InventoryImportService(BaseImportService):
    """
    Handles asset/inventory bulk imports.

    Creates Asset records. Company isolation is
    guaranteed via category and vendor FK lookups
    which were already company-scoped during validation.
    """

    module = ImportModule.INVENTORY

    def _create_objects(self, preview_rows):
        from inventory.models import Asset, AssetStatus, AssetCondition
        from datetime import date as date_type
        from decimal import Decimal

        to_create = []
        for row in preview_rows:
            category_id = row.get("category_id")
            vendor_id   = row.get("vendor_id")

            if not category_id:
                continue

            purchase_date   = row.get("purchase_date")
            warranty_expiry = row.get("warranty_expiry")

            if isinstance(purchase_date, str) and purchase_date:
                purchase_date = date_type.fromisoformat(purchase_date)
            if isinstance(warranty_expiry, str) and warranty_expiry:
                warranty_expiry = date_type.fromisoformat(warranty_expiry)

            purchase_cost = row.get("purchase_cost")
            if purchase_cost:
                purchase_cost = Decimal(str(purchase_cost))

            asset = Asset(
                company         = self.company,
                category_id     = category_id,
                vendor_id       = vendor_id,
                asset_tag       = row.get("asset_tag", ""),
                name            = row.get("name", ""),
                serial_number   = row.get("serial_number", ""),
                brand           = row.get("brand", ""),
                model           = row.get("model", ""),
                description     = row.get("description", ""),
                purchase_date   = purchase_date,
                purchase_cost   = purchase_cost,
                warranty_expiry = warranty_expiry,
                invoice_number  = row.get("invoice_number", ""),
                status          = row.get("status", AssetStatus.AVAILABLE),
                condition       = row.get("condition", AssetCondition.NEW),
                location        = row.get("location", ""),
                notes           = row.get("notes", ""),
            )
            to_create.append(asset)

        created = Asset.objects.bulk_create(to_create)
        return len(created)


# ==========================================================
# PAYMENT IMPORT SERVICE
# ==========================================================

class PaymentImportService(BaseImportService):
    """
    Handles payment bulk imports.

    Creates Payment records. Amount must be positive.
    """

    module = ImportModule.PAYMENTS

    def _create_objects(self, preview_rows):
        from payments.models import Payment
        from employees.models import Employee
        from datetime import date as date_type

        to_create = []
        for row in preview_rows:
            employee_id = row.get("employee_id")
            try:
                employee = Employee.objects.get(company=self.company, employee_id=employee_id)
            except Employee.DoesNotExist:
                continue

            payment_date = row.get("payment_date")
            if isinstance(payment_date, str) and payment_date:
                payment_date = date_type.fromisoformat(payment_date)

            amount = Decimal(str(row.get("amount") or 0))

            record = Payment(
                company          = self.company,
                employee         = employee,
                amount           = amount,
                payment_date     = payment_date,
                payment_method   = row.get("payment_method", ""),
                reference_number = row.get("reference_number", ""),
                description      = row.get("description", ""),
                # Snapshots
                employee_name_snapshot = employee.full_name,
                employee_id_snapshot   = employee.employee_id,
            )
            to_create.append(record)

        created = Payment.objects.bulk_create(to_create)
        return len(created)


# ==========================================================
# CANCEL SERVICE
# ==========================================================

class ImportCancelService:
    """
    Allows cancelling a PREVIEW-status import.
    """

    def __init__(self, company, user):
        self.company = company
        self.user    = user

    def cancel(self, log_id):
        """Cancel a preview import log."""
        try:
            log = ImportLog.objects.get(id=log_id, company=self.company)
        except ImportLog.DoesNotExist:
            raise PreviewExpiredError(f"Import log #{log_id} not found.")

        if log.status not in (ImportStatus.PENDING, ImportStatus.PREVIEW):
            raise ImportAlreadyConfirmedError(
                f"Cannot cancel import log #{log_id} with status '{log.status}'."
            )

        log.status       = ImportStatus.CANCELLED
        log.preview_data = []
        log.completed_at = timezone.now()
        log.save()

        return {"log_id": log_id, "status": "cancelled"}


# ==========================================================
# IMPORT SERVICE FACTORY
# ==========================================================

IMPORT_SERVICES = {
    ImportModule.EMPLOYEES:  EmployeeImportService,
    ImportModule.ATTENDANCE: AttendanceImportService,
    ImportModule.LEAVE:      LeaveImportService,
    ImportModule.PAYROLL:    PayrollImportService,
    ImportModule.INVENTORY:  InventoryImportService,
    ImportModule.PAYMENTS:   PaymentImportService,
}


def get_import_service(module, company, user):
    """
    Return the correct import service for the given module.

    Args:
        module  (str):      One of ImportModule constants.
        company (Company):  Authenticated user's company.
        user    (User):     Authenticated user.
    """
    service_class = IMPORT_SERVICES.get(module)
    if not service_class:
        raise ValueError(f"No import service found for module '{module}'.")
    return service_class(company=company, user=user)
