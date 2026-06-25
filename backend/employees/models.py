from django.db import models
from django.core.exceptions import ValidationError

from company.models import Company


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
        """
        Validate department data.
        """

        super().clean()

        if self.department_name is not None:
            self.department_name = self.department_name.strip()

        if self.department_code is not None:
            self.department_code = self.department_code.strip()

        if not self.department_name:
            raise ValidationError(
                {
                    "department_name":
                    "Department name is required."
                }
            )

        if not self.department_code:
            raise ValidationError(
                {
                    "department_code":
                    "Department code is required."
                }
            )

    def save(self, *args, **kwargs):
        """
        Normalize values before saving.
        """

        if self.department_name:
            self.department_name = (
                self.department_name.strip()
            )

        if self.department_code:
            self.department_code = (
                self.department_code.strip().upper()
            )

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.company.company_name} - "
            f"{self.department_name}"
        )


# ==========================================================
# DESIGNATION MODEL
# ==========================================================

class Designation(models.Model):
    """
    Represents an employee designation
    within a company.

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
        """
        Validate designation data.
        """

        super().clean()

        if self.designation_name is not None:
            self.designation_name = (
                self.designation_name.strip()
            )

        if self.designation_code is not None:
            self.designation_code = (
                self.designation_code.strip()
            )

        if not self.designation_name:
            raise ValidationError(
                {
                    "designation_name":
                    "Designation name is required."
                }
            )

        if not self.designation_code:
            raise ValidationError(
                {
                    "designation_code":
                    "Designation code is required."
                }
            )

    def save(self, *args, **kwargs):
        """
        Normalize values before saving.
        """

        if self.designation_name:
            self.designation_name = (
                self.designation_name.strip()
            )

        if self.designation_code:
            self.designation_code = (
                self.designation_code.strip().upper()
            )

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.company.company_name} - "
            f"{self.designation_name}"
        )