from django.db import models
from django.core.exceptions import ValidationError

from company.models import Company



# ==========================================================
# HOLIDAY TYPE
# ==========================================================

class HolidayType(models.TextChoices):
    NATIONAL = "National", "National Holiday"
    FESTIVAL = "Festival", "Festival"
    COMPANY = "Company", "Company Holiday"
    OPTIONAL = "Optional", "Optional Holiday"
    OTHER = "Other", "Other"



# ==========================================================
# HOLIDAY MODEL
# ==========================================================

class Holiday(models.Model):
    """
    Stores holidays for a company.

    Used by:
    - Attendance
    - Leave Management
    - Payroll
    - Reports
    - AI Analytics
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="holidays",
    )

    name = models.CharField(
        max_length=150,
    )

    date = models.DateField()

    holiday_type = models.CharField(
        max_length=20,
        choices=HolidayType.choices,
        default=HolidayType.NATIONAL,
    )

    description = models.TextField(
        blank=True,
    )

    is_optional = models.BooleanField(
        default=False,
        help_text="Employees may choose to take this holiday.",
    )

    is_recurring = models.BooleanField(
        default=True,
        help_text="Whether this holiday repeats every year.",
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

        ordering = (
            "date",
            "name",
        )

        verbose_name = "Holiday"

        verbose_name_plural = "Holidays"

        constraints = [

            models.UniqueConstraint(
                fields=(
                    "company",
                    "date",
                ),
                name="unique_holiday_per_company_per_date",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["date"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    def clean(self):
        """
        Business validation.
        """

        super().clean()

        self.name = self.name.strip()

        self.description = self.description.strip()

        if not self.name:

            raise ValidationError(
                {
                    "name":
                    "Holiday name cannot be empty."
                }
            )

    def save(
        self,
        *args,
        **kwargs,
    ):

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return (
            f"{self.name}"
            f" ({self.date})"
        )