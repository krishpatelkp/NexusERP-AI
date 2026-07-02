"""
==========================================================
NexusERP-AI  |  data_exchange  |  constants.py
==========================================================

Single source of truth for all module names,
column definitions, choices, and limits used
across the entire Data Exchange Framework.

Rules:
- Never hardcode module names in service/view files.
- Always import from here.
- Adding a new module = add it here only.
==========================================================
"""

# ==========================================================
# SUPPORTED MODULES
# ==========================================================

class ImportModule:
    EMPLOYEES   = "employees"
    ATTENDANCE  = "attendance"
    LEAVE       = "leave"
    PAYROLL     = "payroll"
    INVENTORY   = "inventory"
    PAYMENTS    = "payments"

    CHOICES = [
        (EMPLOYEES,  "Employees"),
        (ATTENDANCE, "Attendance"),
        (LEAVE,      "Leave"),
        (PAYROLL,    "Payroll"),
        (INVENTORY,  "Inventory"),
        (PAYMENTS,   "Payments"),
    ]

    ALL = [EMPLOYEES, ATTENDANCE, LEAVE, PAYROLL, INVENTORY, PAYMENTS]


class ExportModule:
    EMPLOYEES   = "employees"
    ATTENDANCE  = "attendance"
    LEAVE       = "leave"
    PAYROLL     = "payroll"
    INVENTORY   = "inventory"
    PAYMENTS    = "payments"

    CHOICES = [
        (EMPLOYEES,  "Employees"),
        (ATTENDANCE, "Attendance"),
        (LEAVE,      "Leave"),
        (PAYROLL,    "Payroll"),
        (INVENTORY,  "Inventory"),
        (PAYMENTS,   "Payments"),
    ]

    ALL = [EMPLOYEES, ATTENDANCE, LEAVE, PAYROLL, INVENTORY, PAYMENTS]


# ==========================================================
# IMPORT LOG STATUS
# ==========================================================

class ImportStatus:
    PENDING    = "pending"
    PREVIEW    = "preview"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"
    CANCELLED  = "cancelled"

    CHOICES = [
        (PENDING,    "Pending"),
        (PREVIEW,    "Preview"),
        (PROCESSING, "Processing"),
        (COMPLETED,  "Completed"),
        (FAILED,     "Failed"),
        (CANCELLED,  "Cancelled"),
    ]


class ExportStatus:
    PENDING   = "pending"
    COMPLETED = "completed"
    FAILED    = "failed"

    CHOICES = [
        (PENDING,   "Pending"),
        (COMPLETED, "Completed"),
        (FAILED,    "Failed"),
    ]


class ExportFormat:
    EXCEL = "excel"
    CSV   = "csv"
    PDF   = "pdf"

    CHOICES = [
        (EXCEL, "Excel (.xlsx)"),
        (CSV,   "CSV (.csv)"),
        (PDF,   "PDF (.pdf)"),
    ]


# ==========================================================
# COLUMN DEFINITIONS PER MODULE
# Required columns that MUST exist in uploaded file.
# ==========================================================

EMPLOYEE_REQUIRED_COLUMNS = [
    "first_name",
    "last_name",
    "email",
    "phone",
    "gender",
    "date_of_birth",
    "marital_status",
    "department",
    "designation",
    "employment_type",
    "joining_date",
    "basic_salary",
]

EMPLOYEE_OPTIONAL_COLUMNS = [
    "middle_name",
    "alternate_phone",
    "blood_group",
    "employee_status",
    "confirmation_date",
]

EMPLOYEE_ALL_COLUMNS = EMPLOYEE_REQUIRED_COLUMNS + EMPLOYEE_OPTIONAL_COLUMNS

# ----------

ATTENDANCE_REQUIRED_COLUMNS = [
    "employee_id",
    "date",
    "status",
]

ATTENDANCE_OPTIONAL_COLUMNS = [
    "check_in",
    "check_out",
    "remarks",
]

ATTENDANCE_ALL_COLUMNS = ATTENDANCE_REQUIRED_COLUMNS + ATTENDANCE_OPTIONAL_COLUMNS

# ----------

LEAVE_REQUIRED_COLUMNS = [
    "employee_id",
    "leave_type",
    "start_date",
    "end_date",
    "reason",
]

LEAVE_OPTIONAL_COLUMNS = [
    "is_half_day",
    "remarks",
]

LEAVE_ALL_COLUMNS = LEAVE_REQUIRED_COLUMNS + LEAVE_OPTIONAL_COLUMNS

# ----------

PAYROLL_REQUIRED_COLUMNS = [
    "employee_id",
    "month",
    "year",
    "basic_salary",
]

PAYROLL_OPTIONAL_COLUMNS = [
    "hra",
    "transport_allowance",
    "other_allowance",
    "pf_deduction",
    "tax_deduction",
    "other_deduction",
]

PAYROLL_ALL_COLUMNS = PAYROLL_REQUIRED_COLUMNS + PAYROLL_OPTIONAL_COLUMNS

# ----------

INVENTORY_REQUIRED_COLUMNS = [
    "asset_tag",
    "name",
    "category",
    "status",
]

INVENTORY_OPTIONAL_COLUMNS = [
    "vendor",
    "serial_number",
    "brand",
    "model",
    "description",
    "purchase_date",
    "purchase_cost",
    "warranty_expiry",
    "location",
    "condition",
    "invoice_number",
]

INVENTORY_ALL_COLUMNS = INVENTORY_REQUIRED_COLUMNS + INVENTORY_OPTIONAL_COLUMNS

# ----------

PAYMENT_REQUIRED_COLUMNS = [
    "employee_id",
    "amount",
    "payment_date",
    "payment_method",
]

PAYMENT_OPTIONAL_COLUMNS = [
    "reference_number",
    "description",
]

PAYMENT_ALL_COLUMNS = PAYMENT_REQUIRED_COLUMNS + PAYMENT_OPTIONAL_COLUMNS

# ==========================================================
# COLUMN MAP  (module → required + optional columns)
# ==========================================================

MODULE_COLUMNS = {
    ImportModule.EMPLOYEES:  {
        "required": EMPLOYEE_REQUIRED_COLUMNS,
        "optional": EMPLOYEE_OPTIONAL_COLUMNS,
        "all":      EMPLOYEE_ALL_COLUMNS,
    },
    ImportModule.ATTENDANCE: {
        "required": ATTENDANCE_REQUIRED_COLUMNS,
        "optional": ATTENDANCE_OPTIONAL_COLUMNS,
        "all":      ATTENDANCE_ALL_COLUMNS,
    },
    ImportModule.LEAVE: {
        "required": LEAVE_REQUIRED_COLUMNS,
        "optional": LEAVE_OPTIONAL_COLUMNS,
        "all":      LEAVE_ALL_COLUMNS,
    },
    ImportModule.PAYROLL: {
        "required": PAYROLL_REQUIRED_COLUMNS,
        "optional": PAYROLL_OPTIONAL_COLUMNS,
        "all":      PAYROLL_ALL_COLUMNS,
    },
    ImportModule.INVENTORY: {
        "required": INVENTORY_REQUIRED_COLUMNS,
        "optional": INVENTORY_OPTIONAL_COLUMNS,
        "all":      INVENTORY_ALL_COLUMNS,
    },
    ImportModule.PAYMENTS: {
        "required": PAYMENT_REQUIRED_COLUMNS,
        "optional": PAYMENT_OPTIONAL_COLUMNS,
        "all":      PAYMENT_ALL_COLUMNS,
    },
}

# ==========================================================
# EXAMPLE ROWS (used in template generation)
# ==========================================================

EMPLOYEE_EXAMPLE_ROW = {
    "first_name":       "John",
    "last_name":        "Doe",
    "middle_name":      "William",
    "email":            "john.doe@example.com",
    "phone":            "9876543210",
    "alternate_phone":  "",
    "gender":           "Male",
    "date_of_birth":    "1990-05-15",
    "marital_status":   "Married",
    "blood_group":      "B+",
    "department":       "Engineering",
    "designation":      "Software Engineer",
    "employment_type":  "Full-Time",
    "employee_status":  "Active",
    "joining_date":     "2023-01-01",
    "confirmation_date":"2023-04-01",
    "basic_salary":     "50000",
}

ATTENDANCE_EXAMPLE_ROW = {
    "employee_id": "EMP000001",
    "date":        "2026-06-01",
    "check_in":    "09:00",
    "check_out":   "18:00",
    "status":      "Present",
    "remarks":     "",
}

LEAVE_EXAMPLE_ROW = {
    "employee_id": "EMP000001",
    "leave_type":  "Sick Leave",
    "start_date":  "2026-06-10",
    "end_date":    "2026-06-11",
    "reason":      "Fever",
    "is_half_day": "No",
    "remarks":     "",
}

PAYROLL_EXAMPLE_ROW = {
    "employee_id":          "EMP000001",
    "month":                "6",
    "year":                 "2026",
    "basic_salary":         "50000",
    "hra":                  "10000",
    "transport_allowance":  "2000",
    "other_allowance":      "0",
    "pf_deduction":         "6000",
    "tax_deduction":        "0",
    "other_deduction":      "0",
}

INVENTORY_EXAMPLE_ROW = {
    "asset_tag":      "LAP-0001",
    "name":           "Dell Latitude 5420",
    "category":       "Laptop",
    "vendor":         "Dell India",
    "serial_number":  "SN-ABC123",
    "brand":          "Dell",
    "model":          "Latitude 5420",
    "description":    "Work laptop",
    "purchase_date":  "2024-01-15",
    "purchase_cost":  "75000",
    "warranty_expiry":"2027-01-14",
    "location":       "IT Store",
    "status":         "Available",
    "condition":      "New",
    "invoice_number": "INV-2024-001",
}

PAYMENT_EXAMPLE_ROW = {
    "employee_id":      "EMP000001",
    "amount":           "55000",
    "payment_date":     "2026-06-30",
    "payment_method":   "Bank Transfer",
    "reference_number": "TXN-20260630-001",
    "description":      "June 2026 Salary",
}

EXAMPLE_ROWS = {
    ImportModule.EMPLOYEES:  EMPLOYEE_EXAMPLE_ROW,
    ImportModule.ATTENDANCE: ATTENDANCE_EXAMPLE_ROW,
    ImportModule.LEAVE:      LEAVE_EXAMPLE_ROW,
    ImportModule.PAYROLL:    PAYROLL_EXAMPLE_ROW,
    ImportModule.INVENTORY:  INVENTORY_EXAMPLE_ROW,
    ImportModule.PAYMENTS:   PAYMENT_EXAMPLE_ROW,
}

# ==========================================================
# VALIDATION LIMITS
# ==========================================================

MAX_IMPORT_ROWS      = 10_000   # Refuse files larger than this
MAX_FILE_SIZE_MB     = 10       # MB
SUPPORTED_EXTENSIONS = [".xlsx", ".csv"]

# ==========================================================
# TEMPLATE FILE NAMES
# ==========================================================

TEMPLATE_FILENAMES = {
    ImportModule.EMPLOYEES:  "nexus_employees_template.xlsx",
    ImportModule.ATTENDANCE: "nexus_attendance_template.xlsx",
    ImportModule.LEAVE:      "nexus_leave_template.xlsx",
    ImportModule.PAYROLL:    "nexus_payroll_template.xlsx",
    ImportModule.INVENTORY:  "nexus_inventory_template.xlsx",
    ImportModule.PAYMENTS:   "nexus_payments_template.xlsx",
}

# ==========================================================
# CHOICE HINTS (used inside template Instruction sheets)
# ==========================================================

CHOICE_HINTS = {
    "gender":           ["Male", "Female", "Other"],
    "marital_status":   ["Single", "Married", "Divorced", "Widowed"],
    "blood_group":      ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "employment_type":  ["Full-Time", "Part-Time", "Contract", "Intern"],
    "employee_status":  ["Active", "Probation", "On Leave", "Resigned", "Terminated", "Retired"],
    "status_attendance":["Present", "Absent", "Half Day", "Leave", "Holiday", "Week Off", "Work From Home"],
    "is_half_day":      ["Yes", "No"],
    "status_inventory": ["Available", "Assigned", "Maintenance", "Lost", "Damaged", "Retired"],
    "condition":        ["New", "Good", "Fair", "Poor"],
    "payment_method":   ["Bank Transfer", "Cheque", "Cash", "UPI", "NEFT", "RTGS", "IMPS"],
}
