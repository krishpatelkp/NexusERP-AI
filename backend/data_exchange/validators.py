"""
==========================================================
NexusERP-AI  |  data_exchange  |  validators.py
==========================================================

Validation layer ONLY.

Responsibilities:
  - Check required columns are present
  - Validate every cell in every row
  - Check FK integrity (department, designation, etc.)
  - Enforce company isolation
  - Detect duplicates within the file and in the DB
  - Return structured error/warning lists

Rules:
  - NO saving to the database
  - NO business logic (that belongs in services.py)
  - Returns (cleaned_rows, errors, warnings)
  - Collect ALL errors — never stop at first error
==========================================================
"""

from datetime import date

from .constants import (
    MODULE_COLUMNS,
    ImportModule,
    CHOICE_HINTS,
)
from .exceptions import MissingColumnsError
from .utils import (
    parse_date,
    parse_decimal,
    parse_int,
    parse_bool,
    parse_time,
    clean_string,
    make_error,
    make_warning,
    normalise_headers,
)


# ==========================================================
# BASE VALIDATOR
# ==========================================================

class BaseValidator:
    """
    Base class for all module validators.

    Subclasses implement _validate_row() which receives
    the raw row dict and the 1-based row index.
    """

    module = None  # Set by subclasses

    def __init__(self, company):
        self.company = company
        self._errors   = []
        self._warnings = []

    # ──────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────

    def validate(self, raw_rows):
        """
        Validate all rows from the uploaded file.

        Args:
            raw_rows (list[dict]): Rows from importer (normalised headers).

        Returns:
            tuple:
                cleaned_rows (list[dict])  — validated & coerced rows
                errors       (list[dict])  — structured error dicts
                warnings     (list[dict])  — structured warning dicts
        """
        self._check_required_columns(raw_rows)
        cleaned_rows = []

        for idx, row in enumerate(raw_rows, start=2):  # row 1 = header
            cleaned, row_errors, row_warnings = self._validate_row(row, idx)
            self._errors   += row_errors
            self._warnings += row_warnings
            if not row_errors:
                cleaned_rows.append(cleaned)

        return cleaned_rows, self._errors, self._warnings

    # ──────────────────────────────────────
    # COLUMN HEADER CHECK
    # ──────────────────────────────────────

    def _check_required_columns(self, rows):
        """
        Raise MissingColumnsError if required columns are absent.
        """
        if not rows:
            return

        file_columns  = set(rows[0].keys())
        required      = set(MODULE_COLUMNS[self.module]["required"])
        missing       = required - file_columns

        if missing:
            raise MissingColumnsError(sorted(missing))

    # ──────────────────────────────────────
    # ROW VALIDATION  (override in subclass)
    # ──────────────────────────────────────

    def _validate_row(self, row, row_num):
        """
        Validate a single row.

        Returns:
            (cleaned_dict, row_errors, row_warnings)
        """
        raise NotImplementedError

    # ──────────────────────────────────────
    # SHARED HELPERS
    # ──────────────────────────────────────

    def _required(self, row, row_num, field, errors):
        """Return the value if present and non-empty; append error if not."""
        value = clean_string(row.get(field, ""))
        if not value:
            errors.append(make_error(
                row_num, field,
                f"'{field}' is required and cannot be empty."
            ))
        return value

    def _optional(self, row, field, default=""):
        """Return the value or default if missing/blank."""
        return clean_string(row.get(field, "")) or default

    def _resolve_department(self, name, row_num, errors):
        """
        Resolve department_name → Department instance.
        Company-scoped. Appends error on miss.
        """
        from employees.models import Department
        try:
            return Department.objects.get(
                company=self.company,
                department_name__iexact=name,
            )
        except Department.DoesNotExist:
            errors.append(make_error(
                row_num, "department",
                f"Department '{name}' does not exist in your company. "
                "Please create it first or check the spelling."
            ))
            return None

    def _resolve_designation(self, name, row_num, errors):
        """Resolve designation_name → Designation. Company-scoped."""
        from employees.models import Designation
        try:
            return Designation.objects.get(
                company=self.company,
                designation_name__iexact=name,
            )
        except Designation.DoesNotExist:
            errors.append(make_error(
                row_num, "designation",
                f"Designation '{name}' does not exist in your company. "
                "Please create it first or check the spelling."
            ))
            return None

    def _resolve_employee(self, employee_id, row_num, errors):
        """Resolve employee_id → Employee. Company-scoped."""
        from employees.models import Employee
        try:
            return Employee.objects.get(
                company=self.company,
                employee_id=employee_id,
            )
        except Employee.DoesNotExist:
            errors.append(make_error(
                row_num, "employee_id",
                f"Employee ID '{employee_id}' does not exist in your company."
            ))
            return None

    def _resolve_leave_type(self, name, row_num, errors):
        """Resolve leave_type name → LeaveType. Company-scoped."""
        from leave_management.models import LeaveType
        try:
            return LeaveType.objects.get(
                company=self.company,
                leave_name__iexact=name,
                is_active=True,
            )
        except LeaveType.DoesNotExist:
            errors.append(make_error(
                row_num, "leave_type",
                f"Leave type '{name}' does not exist or is inactive."
            ))
            return None

    def _resolve_asset_category(self, name, row_num, errors):
        """Resolve category name → AssetCategory. Company-scoped."""
        from inventory.models import AssetCategory
        try:
            return AssetCategory.objects.get(
                company=self.company,
                name__iexact=name,
                is_active=True,
            )
        except AssetCategory.DoesNotExist:
            errors.append(make_error(
                row_num, "category",
                f"Asset category '{name}' does not exist. "
                "Please create it first."
            ))
            return None

    def _resolve_vendor(self, name, row_num, errors):
        """Resolve vendor name → Vendor. Company-scoped."""
        if not name:
            return None
        from inventory.models import Vendor
        try:
            return Vendor.objects.get(
                company=self.company,
                name__iexact=name,
                is_active=True,
            )
        except Vendor.DoesNotExist:
            errors.append(make_error(
                row_num, "vendor",
                f"Vendor '{name}' does not exist. "
                "Please create it first or leave blank."
            ))
            return None

    def _validate_choice(self, value, field, choices, row_num, errors):
        """Check that value is in the allowed choices list."""
        if value and value not in choices:
            errors.append(make_error(
                row_num, field,
                f"'{value}' is not a valid value for '{field}'. "
                f"Allowed values: {', '.join(choices)}."
            ))
            return False
        return True

    def _validate_positive_decimal(self, value, field, row_num, errors):
        """Parse decimal and ensure it is non-negative."""
        try:
            parsed = parse_decimal(value)
            if parsed is not None and parsed < 0:
                errors.append(make_error(
                    row_num, field,
                    f"'{field}' cannot be negative. Got: {value}."
                ))
                return None
            return parsed
        except ValueError as exc:
            errors.append(make_error(row_num, field, str(exc)))
            return None

    def _validate_date(self, value, field, row_num, errors, required=False):
        """Parse date field. Append error on failure."""
        try:
            parsed = parse_date(value)
            if required and parsed is None:
                errors.append(make_error(
                    row_num, field,
                    f"'{field}' is required."
                ))
            return parsed
        except ValueError as exc:
            errors.append(make_error(row_num, field, str(exc)))
            return None


# ==========================================================
# EMPLOYEE VALIDATOR
# ==========================================================

class EmployeeValidator(BaseValidator):
    """
    Validates employee import rows.

    Checks:
      - Required fields present and non-empty
      - Email uniqueness (within file + DB)
      - Department and Designation exist
      - Valid enum values
      - Date fields parseable
      - Salary non-negative
    """

    module = ImportModule.EMPLOYEES

    def __init__(self, company):
        super().__init__(company)
        self._seen_emails = set()  # Intra-file duplicate check

    def _validate_row(self, row, row_num):
        errors   = []
        warnings = []
        cleaned  = {}

        # Required strings
        for field in ["first_name", "last_name", "phone", "gender",
                      "marital_status", "employment_type"]:
            val = self._required(row, row_num, field, errors)
            cleaned[field] = val

        cleaned["middle_name"]     = self._optional(row, "middle_name")
        cleaned["alternate_phone"] = self._optional(row, "alternate_phone")
        cleaned["blood_group"]     = self._optional(row, "blood_group")

        # Email
        email = self._required(row, row_num, "email", errors)
        if email:
            if email.lower() in self._seen_emails:
                errors.append(make_error(
                    row_num, "email",
                    f"Duplicate email '{email}' found in this file."
                ))
            else:
                from employees.models import Employee
                if Employee.objects.filter(
                    company=self.company,
                    email__iexact=email,
                ).exists():
                    errors.append(make_error(
                        row_num, "email",
                        f"Employee with email '{email}' already exists."
                    ))
                else:
                    self._seen_emails.add(email.lower())
            cleaned["email"] = email

        # Enum validations
        self._validate_choice(
            cleaned.get("gender"), "gender",
            CHOICE_HINTS["gender"], row_num, errors,
        )
        self._validate_choice(
            cleaned.get("marital_status"), "marital_status",
            CHOICE_HINTS["marital_status"], row_num, errors,
        )
        self._validate_choice(
            cleaned.get("employment_type"), "employment_type",
            CHOICE_HINTS["employment_type"], row_num, errors,
        )
        if cleaned.get("blood_group"):
            self._validate_choice(
                cleaned["blood_group"], "blood_group",
                CHOICE_HINTS["blood_group"], row_num, errors,
            )

        # Dates
        cleaned["date_of_birth"] = self._validate_date(
            row.get("date_of_birth"), "date_of_birth", row_num, errors, required=True,
        )
        cleaned["joining_date"] = self._validate_date(
            row.get("joining_date"), "joining_date", row_num, errors, required=True,
        )
        cleaned["confirmation_date"] = self._validate_date(
            row.get("confirmation_date"), "confirmation_date", row_num, errors,
        )

        # Salary
        cleaned["basic_salary"] = self._validate_positive_decimal(
            row.get("basic_salary"), "basic_salary", row_num, errors,
        )

        # Employee status
        emp_status = self._optional(row, "employee_status", "Probation")
        self._validate_choice(
            emp_status, "employee_status",
            CHOICE_HINTS["employee_status"], row_num, errors,
        )
        cleaned["employee_status"] = emp_status

        # FK lookups
        dept_name = self._required(row, row_num, "department", errors)
        cleaned["department"] = (
            self._resolve_department(dept_name, row_num, errors) if dept_name else None
        )

        desig_name = self._required(row, row_num, "designation", errors)
        cleaned["designation"] = (
            self._resolve_designation(desig_name, row_num, errors) if desig_name else None
        )

        return cleaned, errors, warnings


# ==========================================================
# ATTENDANCE VALIDATOR
# ==========================================================

class AttendanceValidator(BaseValidator):
    """
    Validates attendance import rows.

    Checks:
      - employee_id exists in this company
      - date is valid
      - status is a valid AttendanceStatus
      - check_in / check_out are valid times
      - No duplicate (employee_id, date) in this file or DB
    """

    module = ImportModule.ATTENDANCE

    def __init__(self, company):
        super().__init__(company)
        self._seen_keys = set()  # (employee_id, date)

    def _validate_row(self, row, row_num):
        errors   = []
        warnings = []
        cleaned  = {}

        employee_id = self._required(row, row_num, "employee_id", errors)
        employee    = None
        if employee_id:
            employee = self._resolve_employee(employee_id, row_num, errors)
        cleaned["employee"] = employee

        att_date = self._validate_date(
            row.get("date"), "date", row_num, errors, required=True,
        )
        cleaned["date"] = att_date

        # Duplicate check
        if employee and att_date:
            key = (employee_id, str(att_date))
            if key in self._seen_keys:
                errors.append(make_error(
                    row_num, "date",
                    f"Duplicate attendance record for employee '{employee_id}' on '{att_date}'."
                ))
            else:
                from attendance.models import Attendance
                if Attendance.objects.filter(
                    employee__company=self.company,
                    employee__employee_id=employee_id,
                    date=att_date,
                ).exists():
                    warnings.append(make_warning(
                        row_num, "date",
                        f"Attendance record for '{employee_id}' on '{att_date}' already exists and will be skipped."
                    ))
                else:
                    self._seen_keys.add(key)

        status_val = self._required(row, row_num, "status", errors)
        self._validate_choice(
            status_val, "status",
            CHOICE_HINTS["status_attendance"], row_num, errors,
        )
        cleaned["status"] = status_val

        # Optional times
        try:
            cleaned["check_in"]  = parse_time(row.get("check_in"))
            cleaned["check_out"] = parse_time(row.get("check_out"))
        except ValueError as exc:
            errors.append(make_error(row_num, "check_in", str(exc)))

        cleaned["remarks"] = self._optional(row, "remarks")

        return cleaned, errors, warnings


# ==========================================================
# LEAVE VALIDATOR
# ==========================================================

class LeaveValidator(BaseValidator):
    """
    Validates leave import rows.

    Checks:
      - employee_id exists
      - leave_type exists and is active
      - start_date <= end_date
      - reason not empty
    """

    module = ImportModule.LEAVE

    def _validate_row(self, row, row_num):
        errors   = []
        warnings = []
        cleaned  = {}

        employee_id = self._required(row, row_num, "employee_id", errors)
        cleaned["employee"] = (
            self._resolve_employee(employee_id, row_num, errors) if employee_id else None
        )

        leave_type_name = self._required(row, row_num, "leave_type", errors)
        cleaned["leave_type"] = (
            self._resolve_leave_type(leave_type_name, row_num, errors)
            if leave_type_name else None
        )

        start = self._validate_date(row.get("start_date"), "start_date", row_num, errors, required=True)
        end   = self._validate_date(row.get("end_date"),   "end_date",   row_num, errors, required=True)
        cleaned["start_date"] = start
        cleaned["end_date"]   = end

        if start and end and end < start:
            errors.append(make_error(
                row_num, "end_date",
                "End date cannot be earlier than start date."
            ))

        cleaned["reason"]     = self._required(row, row_num, "reason", errors)
        cleaned["is_half_day"] = False
        try:
            cleaned["is_half_day"] = parse_bool(row.get("is_half_day", "No"))
        except ValueError as exc:
            warnings.append(make_warning(row_num, "is_half_day", str(exc)))

        cleaned["remarks"] = self._optional(row, "remarks")

        return cleaned, errors, warnings


# ==========================================================
# PAYROLL VALIDATOR
# ==========================================================

class PayrollValidator(BaseValidator):
    """
    Validates payroll import rows.

    Checks:
      - employee_id exists
      - month in 1–12, year reasonable
      - All monetary values non-negative
    """

    module = ImportModule.PAYROLL

    def _validate_row(self, row, row_num):
        errors   = []
        warnings = []
        cleaned  = {}

        employee_id = self._required(row, row_num, "employee_id", errors)
        cleaned["employee"] = (
            self._resolve_employee(employee_id, row_num, errors) if employee_id else None
        )

        month = None
        try:
            month = parse_int(row.get("month"))
            if month is None or not (1 <= month <= 12):
                errors.append(make_error(row_num, "month", "Month must be between 1 and 12."))
        except ValueError as exc:
            errors.append(make_error(row_num, "month", str(exc)))
        cleaned["month"] = month

        year = None
        try:
            year = parse_int(row.get("year"))
            current_year = date.today().year
            if year is None or not (2000 <= year <= current_year + 1):
                errors.append(make_error(
                    row_num, "year",
                    f"Year must be between 2000 and {current_year + 1}."
                ))
        except ValueError as exc:
            errors.append(make_error(row_num, "year", str(exc)))
        cleaned["year"] = year

        for field in ["basic_salary", "hra", "transport_allowance",
                      "other_allowance", "pf_deduction", "tax_deduction", "other_deduction"]:
            cleaned[field] = self._validate_positive_decimal(
                row.get(field, 0), field, row_num, errors,
            )

        return cleaned, errors, warnings


# ==========================================================
# INVENTORY VALIDATOR
# ==========================================================

class InventoryValidator(BaseValidator):
    """
    Validates asset/inventory import rows.

    Checks:
      - asset_tag unique within file and DB
      - category exists
      - vendor exists (if provided)
      - status, condition valid choices
    """

    module = ImportModule.INVENTORY

    def __init__(self, company):
        super().__init__(company)
        self._seen_tags = set()

    def _validate_row(self, row, row_num):
        errors   = []
        warnings = []
        cleaned  = {}

        asset_tag = self._required(row, row_num, "asset_tag", errors)
        if asset_tag:
            if asset_tag in self._seen_tags:
                errors.append(make_error(
                    row_num, "asset_tag",
                    f"Duplicate asset tag '{asset_tag}' in this file."
                ))
            else:
                from inventory.models import Asset
                if Asset.objects.filter(
                    company=self.company,
                    asset_tag=asset_tag,
                ).exists():
                    errors.append(make_error(
                        row_num, "asset_tag",
                        f"Asset with tag '{asset_tag}' already exists."
                    ))
                else:
                    self._seen_tags.add(asset_tag)
        cleaned["asset_tag"] = asset_tag

        cleaned["name"] = self._required(row, row_num, "name", errors)

        category_name = self._required(row, row_num, "category", errors)
        cleaned["category"] = (
            self._resolve_asset_category(category_name, row_num, errors)
            if category_name else None
        )

        vendor_name = self._optional(row, "vendor")
        cleaned["vendor"] = (
            self._resolve_vendor(vendor_name, row_num, errors) if vendor_name else None
        )

        status_val = self._optional(row, "status", "Available")
        self._validate_choice(
            status_val, "status",
            CHOICE_HINTS["status_inventory"], row_num, errors,
        )
        cleaned["status"] = status_val

        condition_val = self._optional(row, "condition", "New")
        self._validate_choice(
            condition_val, "condition",
            CHOICE_HINTS["condition"], row_num, errors,
        )
        cleaned["condition"] = condition_val

        for text_field in ["serial_number", "brand", "model", "description", "location", "invoice_number"]:
            cleaned[text_field] = self._optional(row, text_field)

        cleaned["purchase_date"]   = self._validate_date(row.get("purchase_date"),   "purchase_date",   row_num, errors)
        cleaned["warranty_expiry"] = self._validate_date(row.get("warranty_expiry"), "warranty_expiry", row_num, errors)
        cleaned["purchase_cost"]   = self._validate_positive_decimal(row.get("purchase_cost"), "purchase_cost", row_num, errors)

        return cleaned, errors, warnings


# ==========================================================
# PAYMENT VALIDATOR
# ==========================================================

class PaymentValidator(BaseValidator):
    """
    Validates payment import rows.

    Checks:
      - employee_id exists
      - amount > 0
      - payment_date valid
      - payment_method valid choice
    """

    module = ImportModule.PAYMENTS

    def _validate_row(self, row, row_num):
        errors   = []
        warnings = []
        cleaned  = {}

        employee_id = self._required(row, row_num, "employee_id", errors)
        cleaned["employee"] = (
            self._resolve_employee(employee_id, row_num, errors) if employee_id else None
        )

        amount = self._validate_positive_decimal(
            row.get("amount"), "amount", row_num, errors,
        )
        if amount is not None and amount <= 0:
            errors.append(make_error(
                row_num, "amount",
                "Amount must be greater than zero."
            ))
        cleaned["amount"] = amount

        cleaned["payment_date"] = self._validate_date(
            row.get("payment_date"), "payment_date", row_num, errors, required=True,
        )

        payment_method = self._required(row, row_num, "payment_method", errors)
        self._validate_choice(
            payment_method, "payment_method",
            CHOICE_HINTS["payment_method"], row_num, errors,
        )
        cleaned["payment_method"]   = payment_method
        cleaned["reference_number"] = self._optional(row, "reference_number")
        cleaned["description"]      = self._optional(row, "description")

        return cleaned, errors, warnings


# ==========================================================
# VALIDATOR FACTORY
# ==========================================================

VALIDATORS = {
    ImportModule.EMPLOYEES:  EmployeeValidator,
    ImportModule.ATTENDANCE: AttendanceValidator,
    ImportModule.LEAVE:      LeaveValidator,
    ImportModule.PAYROLL:    PayrollValidator,
    ImportModule.INVENTORY:  InventoryValidator,
    ImportModule.PAYMENTS:   PaymentValidator,
}


def get_validator(module, company):
    """
    Return the appropriate validator for the given module.

    Args:
        module  (str):     One of ImportModule constants.
        company (Company): The authenticated user's company.

    Returns:
        BaseValidator subclass instance.
    """
    validator_class = VALIDATORS.get(module)
    if not validator_class:
        raise ValueError(f"No validator found for module '{module}'.")
    return validator_class(company)
