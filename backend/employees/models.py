from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator

from company.models import Company
from accounts.models import User
import re


# ==========================================================
# PHONE VALIDATOR
# ==========================================================

phone_validator = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=(
        "Enter a valid phone number. "
        "Up to 15 digits. "
        "Optionally start with +."
    ),
)


# ==========================================================
# PROFILE PHOTO VALIDATOR
# ==========================================================

def validate_profile_photo(file):
    """
    Validate profile photo file type and size.
    Allowed: JPEG, PNG, WebP
    Max size: 2MB
    """

    valid_types = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    max_size_mb = 2

    if file.content_type not in valid_types:
        raise ValidationError(
            "Only JPEG, PNG and WebP images are allowed."
        )

    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f"Image size must not exceed {max_size_mb}MB."
        )


# ==========================================================
# DEPARTMENT MODEL
# ==========================================================

class Department(models.Model):
    """
    Represents a department within a company.

    Every employee belongs to one department.

    The manager field will be added later after the
    Employee model is created to avoid a circular
    dependency.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="departments",
    )

    department_name = models.CharField(
        max_length=100,
    )

    department_code = models.CharField(
        max_length=20,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "company",
            "department_name",
        ]

        verbose_name = "Department"
        verbose_name_plural = "Departments"

        constraints = [
            models.UniqueConstraint(
                fields=["company", "department_name"],
                name="unique_department_name_per_company",
            ),
            models.UniqueConstraint(
                fields=["company", "department_code"],
                name="unique_department_code_per_company",
            ),
        ]

        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["department_code"]),
            models.Index(fields=["is_active"]),
        ]

    def clean(self):
        super().clean()

        if self.department_name is not None:
            self.department_name = self.department_name.strip()

        if self.department_code is not None:
            self.department_code = self.department_code.strip()

        if not self.department_name:
            raise ValidationError(
                {"department_name": "Department name is required."}
            )

        if not self.department_code:
            raise ValidationError(
                {"department_code": "Department code is required."}
            )

    def save(self, *args, **kwargs):
        if self.department_name:
            self.department_name = self.department_name.strip()

        if self.department_code:
            self.department_code = self.department_code.strip().upper()

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.company_name} - {self.department_name}"


# ==========================================================
# DESIGNATION MODEL
# ==========================================================

class Designation(models.Model):
    """
    Represents an employee designation within a company.

    Examples:
        Software Engineer
        HR Executive
        Team Lead
        Accountant
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="designations",
    )

    designation_name = models.CharField(
        max_length=100,
    )

    designation_code = models.CharField(
        max_length=20,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "company",
            "designation_name",
        ]

        verbose_name = "Designation"
        verbose_name_plural = "Designations"

        constraints = [
            models.UniqueConstraint(
                fields=["company", "designation_name"],
                name="unique_designation_name_per_company",
            ),
            models.UniqueConstraint(
                fields=["company", "designation_code"],
                name="unique_designation_code_per_company",
            ),
        ]

        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["designation_code"]),
            models.Index(fields=["is_active"]),
        ]

    def clean(self):
        super().clean()

        if self.designation_name is not None:
            self.designation_name = self.designation_name.strip()

        if self.designation_code is not None:
            self.designation_code = self.designation_code.strip()

        if not self.designation_name:
            raise ValidationError(
                {"designation_name": "Designation name is required."}
            )

        if not self.designation_code:
            raise ValidationError(
                {"designation_code": "Designation code is required."}
            )

    def save(self, *args, **kwargs):
        if self.designation_name:
            self.designation_name = self.designation_name.strip()

        if self.designation_code:
            self.designation_code = self.designation_code.strip().upper()

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.company_name} - {self.designation_name}"


# ==========================================================
# EMPLOYEE ID GENERATOR
# ==========================================================

def generate_employee_id(company):
    """
    Auto-generates a unique employee ID per company.

    Format: EMP000001, EMP000002, EMP000003 ...

    Uses the highest existing employee_id number
    instead of count() to avoid race conditions
    and gaps caused by rollbacks.
    """

    last = (
        Employee.objects
        .filter(company=company)
        .order_by("-employee_id")
        .values_list("employee_id", flat=True)
        .first()
    )

    if last:
        try:
            last_number = int(last.replace("EMP", ""))
        except ValueError:
            last_number = 0
    else:
        last_number = 0

    return f"EMP{last_number + 1:06d}"


# ==========================================================
# EMPLOYEE MODEL
# ==========================================================

class Employee(models.Model):
    """
    Core employee model for NexusERP.

    Stores all personal, contact, organizational,
    salary and status information for an employee.

    Related models:
        EmployeeAddress     → addresses
        EmployeeBankDetails → bank info
        EmergencyContact    → emergency contacts
        EmployeeDocument    → uploaded documents
    """

    # ──────────────────────────────────────
    # CHOICES
    # ──────────────────────────────────────

    class Gender(models.TextChoices):
        MALE   = "Male",   "Male"
        FEMALE = "Female", "Female"
        OTHER  = "Other",  "Other"

    class MaritalStatus(models.TextChoices):
        SINGLE   = "Single",   "Single"
        MARRIED  = "Married",  "Married"
        DIVORCED = "Divorced", "Divorced"
        WIDOWED  = "Widowed",  "Widowed"

    class BloodGroup(models.TextChoices):
        A_POS  = "A+",  "A+"
        A_NEG  = "A-",  "A-"
        B_POS  = "B+",  "B+"
        B_NEG  = "B-",  "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS  = "O+",  "O+"
        O_NEG  = "O-",  "O-"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "Full-Time", "Full-Time"
        PART_TIME = "Part-Time", "Part-Time"
        CONTRACT  = "Contract",  "Contract"
        INTERN    = "Intern",    "Intern"

    class EmployeeStatus(models.TextChoices):
        ACTIVE     = "Active",     "Active"
        PROBATION  = "Probation",  "Probation"
        ON_LEAVE   = "On Leave",   "On Leave"
        RESIGNED   = "Resigned",   "Resigned"
        TERMINATED = "Terminated", "Terminated"
        RETIRED    = "Retired",    "Retired"

    # ──────────────────────────────────────
    # IDENTIFICATION
    # ──────────────────────────────────────

    employee_id = models.CharField(
        max_length=20,
        editable=False,
        db_index=True,
    )

    # ──────────────────────────────────────
    # PERSONAL INFORMATION
    # ──────────────────────────────────────

    first_name = models.CharField(
        max_length=100,
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True,
    )

    last_name = models.CharField(
        max_length=100,
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )

    date_of_birth = models.DateField()

    marital_status = models.CharField(
        max_length=10,
        choices=MaritalStatus.choices,
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BloodGroup.choices,
        blank=True,
    )

    profile_photo = models.ImageField(
        upload_to="employees/photos/",
        blank=True,
        validators=[validate_profile_photo],
    )

    # ──────────────────────────────────────
    # CONTACT INFORMATION
    # ──────────────────────────────────────

    email = models.EmailField(
        db_index=True,
    )

    phone = models.CharField(
        max_length=15,
        validators=[phone_validator],
    )

    alternate_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[phone_validator],
    )

    # ──────────────────────────────────────
    # ORGANIZATION
    # ──────────────────────────────────────

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employees",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    reporting_manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )

    user_account = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
    )

    employment_type = models.CharField(
        max_length=15,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )

    joining_date = models.DateField()

    confirmation_date = models.DateField(
        null=True,
        blank=True,
    )

    # ──────────────────────────────────────
    # SALARY
    # ──────────────────────────────────────

    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    # ──────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────

    employee_status = models.CharField(
        max_length=15,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.PROBATION,
    )

    is_active = models.BooleanField(
        default=True,
    )

    resignation_date = models.DateField(
        null=True,
        blank=True,
    )

    termination_date = models.DateField(
        null=True,
        blank=True,
    )

    retirement_date = models.DateField(
        null=True,
        blank=True,
    )

    # ──────────────────────────────────────
    # AUDIT
    # ──────────────────────────────────────

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ──────────────────────────────────────
    # META
    # ──────────────────────────────────────

    class Meta:
        ordering = [
            "company",
            "first_name",
            "last_name",
        ]

        verbose_name = "Employee"
        verbose_name_plural = "Employees"

        constraints = [
            models.UniqueConstraint(
                fields=["company", "employee_id"],
                name="unique_employee_id_per_company",
            ),
            models.UniqueConstraint(
                fields=["company", "email"],
                name="unique_employee_email_per_company",
            ),
        ]

        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["employee_id"]),
            models.Index(fields=["department"]),
            models.Index(fields=["designation"]),
            models.Index(fields=["employee_status"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["joining_date"]),
        ]

    # ──────────────────────────────────────
    # CLEAN
    # ──────────────────────────────────────

    def clean(self):
        """
        Validate and normalize employee data.
        """

        super().clean()

        # Normalize text fields
        if self.first_name:
            self.first_name = self.first_name.strip()

        if self.middle_name:
            self.middle_name = self.middle_name.strip()

        if self.last_name:
            self.last_name = self.last_name.strip()

        if self.phone:
            self.phone = self.phone.strip()

        if self.alternate_phone:
            self.alternate_phone = self.alternate_phone.strip()

        # Normalize email
        if self.email:
            self.email = self.email.strip().lower()

        # Required fields
        if not self.first_name:
            raise ValidationError(
                {"first_name": "First name is required."}
            )

        if not self.last_name:
            raise ValidationError(
                {"last_name": "Last name is required."}
            )

        # Department must belong to same company
        if self.department and self.company:
            if self.department.company != self.company:
                raise ValidationError(
                    {
                        "department":
                        "Department does not belong "
                        "to this company."
                    }
                )

        # Designation must belong to same company
        if self.designation and self.company:
            if self.designation.company != self.company:
                raise ValidationError(
                    {
                        "designation":
                        "Designation does not belong "
                        "to this company."
                    }
                )

        # Reporting manager must belong to same company
        if self.reporting_manager and self.company:
            if self.reporting_manager.company != self.company:
                raise ValidationError(
                    {
                        "reporting_manager":
                        "Reporting manager does not "
                        "belong to this company."
                    }
                )

        # Employee cannot be their own manager
        if (
            self.reporting_manager
            and self.pk
            and self.reporting_manager.pk == self.pk
        ):
            raise ValidationError(
                {
                    "reporting_manager":
                    "An employee cannot be "
                    "their own reporting manager."
                }
            )

        # Confirmation date must be after joining date
        if self.confirmation_date and self.joining_date:
            if self.confirmation_date < self.joining_date:
                raise ValidationError(
                    {
                        "confirmation_date":
                        "Confirmation date cannot be "
                        "before joining date."
                    }
                )

        # Resignation date required when status is Resigned
        if (
            self.employee_status == self.EmployeeStatus.RESIGNED
            and not self.resignation_date
        ):
            raise ValidationError(
                {
                    "resignation_date":
                    "Resignation date is required "
                    "when status is Resigned."
                }
            )

        # Termination date required when status is Terminated
        if (
            self.employee_status == self.EmployeeStatus.TERMINATED
            and not self.termination_date
        ):
            raise ValidationError(
                {
                    "termination_date":
                    "Termination date is required "
                    "when status is Terminated."
                }
            )

        # Retirement date required when status is Retired
        if (
            self.employee_status == self.EmployeeStatus.RETIRED
            and not self.retirement_date
        ):
            raise ValidationError(
                {
                    "retirement_date":
                    "Retirement date is required "
                    "when status is Retired."
                }
            )

    # ──────────────────────────────────────
    # SAVE
    # ──────────────────────────────────────

    def save(self, *args, **kwargs):
        """
        Auto-generate employee_id on first save.
        Validate before saving.
        """

        if not self.employee_id:
            self.employee_id = generate_employee_id(
                self.company
            )

        self.full_clean()
        super().save(*args, **kwargs)

    # ──────────────────────────────────────
    # PROPERTIES
    # ──────────────────────────────────────

    @property
    def full_name(self):
        """
        Returns the employee's full name.
        Includes middle name if present.
        """

        parts = [self.first_name]

        if self.middle_name:
            parts.append(self.middle_name)

        parts.append(self.last_name)

        return " ".join(parts)

    # ──────────────────────────────────────
    # STR
    # ──────────────────────────────────────

    def __str__(self):
        return (
            f"{self.employee_id} - "
            f"{self.full_name}"
        )
    

# ==========================================================
# EMPLOYEE ADDRESS MODEL
# ==========================================================

class EmployeeAddress(models.Model):
    """
    Stores employee addresses.

    Every employee can have one Current
    address and one Permanent address.
    """

    class AddressType(models.TextChoices):
        CURRENT = (
            "Current",
            "Current",
        )
        PERMANENT = (
            "Permanent",
            "Permanent",
        )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
    )

    address_line_1 = models.CharField(
        max_length=255,
    )

    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
    )

    state = models.CharField(
        max_length=100,
    )

    country = models.CharField(
        max_length=100,
    )

    postal_code = models.CharField(
        max_length=20,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "employee",
            "address_type",
        ]

        verbose_name = "Employee Address"

        verbose_name_plural = "Employee Addresses"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "employee",
                    "address_type",
                ],
                name="unique_address_type_per_employee",
            ),

        ]

        indexes = [

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["address_type"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    def clean(self):
        """
        Validate address details.
        """

        super().clean()

        text_fields = [

            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "country",
            "postal_code",

        ]

        for field in text_fields:

            value = getattr(
                self,
                field,
            )

            if value is not None:

                setattr(
                    self,
                    field,
                    value.strip(),
                )

        required_fields = {

            "address_line_1":
            "Address Line 1 is required.",

            "city":
            "City is required.",

            "state":
            "State is required.",

            "country":
            "Country is required.",

            "postal_code":
            "Postal code is required.",

        }

        for field, message in required_fields.items():

            if not getattr(
                self,
                field,
            ):
                raise ValidationError(
                    {
                        field: message,
                    }
                )

    def save(self, *args, **kwargs):
        """
        Validate before saving.
        """

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return (
            f"{self.employee.employee_id}"
            f" - "
            f"{self.address_type}"
        )
    


# ==========================================================
# EMERGENCY CONTACT MODEL
# ==========================================================

class EmergencyContact(models.Model):
    """
    Stores emergency contact information
    for employees.

    Every employee can have multiple
    emergency contacts, but only one
    primary emergency contact.
    """

    class Relationship(models.TextChoices):

        FATHER = (
            "Father",
            "Father",
        )

        MOTHER = (
            "Mother",
            "Mother",
        )

        SPOUSE = (
            "Spouse",
            "Spouse",
        )

        BROTHER = (
            "Brother",
            "Brother",
        )

        SISTER = (
            "Sister",
            "Sister",
        )

        GUARDIAN = (
            "Guardian",
            "Guardian",
        )

        FRIEND = (
            "Friend",
            "Friend",
        )

        OTHER = (
            "Other",
            "Other",
        )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )

    contact_name = models.CharField(
        max_length=100,
    )

    relationship = models.CharField(
        max_length=20,
        choices=Relationship.choices,
    )

    phone = models.CharField(
        max_length=15,
    )

    alternate_phone = models.CharField(
        max_length=15,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "employee",
            "-is_primary",
            "contact_name",
        ]

        verbose_name = "Emergency Contact"

        verbose_name_plural = (
            "Emergency Contacts"
        )

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "employee",
                    "phone",
                ],
                name="unique_emergency_phone_per_employee",
            ),

        ]

        indexes = [

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["relationship"],
            ),

            models.Index(
                fields=["phone"],
            ),

            models.Index(
                fields=["is_primary"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    def clean(self):
        """
        Validate emergency contact data.
        """

        super().clean()

        text_fields = [

            "contact_name",
            "phone",
            "alternate_phone",
            "address",

        ]

        for field in text_fields:

            value = getattr(
                self,
                field,
            )

            if value is not None:

                setattr(
                    self,
                    field,
                    value.strip(),
                )

        if not self.contact_name:

            raise ValidationError(
                {
                    "contact_name":
                    "Contact name is required."
                }
            )

        if not self.phone:

            raise ValidationError(
                {
                    "phone":
                    "Phone number is required."
                }
            )

        if self.is_primary:

            queryset = (
                EmergencyContact.objects.filter(
                    employee=self.employee,
                    is_primary=True,
                )
            )

            if self.pk:

                queryset = queryset.exclude(
                    pk=self.pk,
                )

            if queryset.exists():

                raise ValidationError(
                    {
                        "is_primary":
                        (
                            "Only one primary "
                            "emergency contact "
                            "is allowed."
                        )
                    }
                )

    def save(
        self,
        *args,
        **kwargs,
    ):
        """
        Validate before saving.
        """

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return (
            f"{self.employee.employee_id}"
            f" - "
            f"{self.contact_name}"
        )
    

# ==========================================================
# EMPLOYEE BANK DETAIL MODEL
# ==========================================================

class EmployeeBankDetail(models.Model):
    """
    Stores employee bank account details.

    Every employee can have multiple
    bank accounts, but only one
    primary account.
    """

    class AccountType(models.TextChoices):

        SAVINGS = (
            "Savings",
            "Savings",
        )

        CURRENT = (
            "Current",
            "Current",
        )

        SALARY = (
            "Salary",
            "Salary",
        )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="bank_details",
    )

    bank_name = models.CharField(
        max_length=100,
    )

    account_holder_name = models.CharField(
        max_length=150,
    )

    account_number = models.CharField(
        max_length=30,
    )

    ifsc_code = models.CharField(
        max_length=11,
    )

    branch_name = models.CharField(
        max_length=100,
    )

    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
    )

    upi_id = models.CharField(
        max_length=100,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "employee",
            "-is_primary",
            "bank_name",
        ]

        verbose_name = "Employee Bank Detail"

        verbose_name_plural = (
            "Employee Bank Details"
        )

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "employee",
                    "account_number",
                ],
                name="unique_bank_account_per_employee",
            ),

        ]

        indexes = [

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["account_number"],
            ),

            models.Index(
                fields=["ifsc_code"],
            ),

            models.Index(
                fields=["is_primary"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    def clean(self):
        """
        Validate bank details.
        """

        super().clean()

        text_fields = [

            "bank_name",
            "account_holder_name",
            "account_number",
            "branch_name",
            "upi_id",

        ]

        for field in text_fields:

            value = getattr(
                self,
                field,
            )

            if value is not None:

                setattr(
                    self,
                    field,
                    value.strip(),
                )

        self.ifsc_code = (
            self.ifsc_code.strip().upper()
        )

        if not self.bank_name:

            raise ValidationError(
                {
                    "bank_name":
                    "Bank name is required."
                }
            )

        if not self.account_holder_name:

            raise ValidationError(
                {
                    "account_holder_name":
                    "Account holder name is required."
                }
            )

        if not self.account_number:

            raise ValidationError(
                {
                    "account_number":
                    "Account number is required."
                }
            )

        if not self.branch_name:

            raise ValidationError(
                {
                    "branch_name":
                    "Branch name is required."
                }
            )

        if not re.match(
            r"^[A-Z]{4}0[A-Z0-9]{6}$",
            self.ifsc_code,
        ):

            raise ValidationError(
                {
                    "ifsc_code":
                    (
                        "Enter a valid "
                        "IFSC code."
                    )
                }
            )

        if self.is_primary:

            queryset = (
                EmployeeBankDetail.objects.filter(
                    employee=self.employee,
                    is_primary=True,
                )
            )

            if self.pk:

                queryset = queryset.exclude(
                    pk=self.pk,
                )

            if queryset.exists():

                raise ValidationError(
                    {
                        "is_primary":
                        (
                            "Only one primary "
                            "bank account is allowed."
                        )
                    }
                )

    def save(
        self,
        *args,
        **kwargs,
    ):
        """
        Validate before saving.
        """

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return (
            f"{self.employee.employee_id}"
            f" - "
            f"{self.bank_name}"
        )