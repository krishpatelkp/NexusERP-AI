from rest_framework import serializers

from .models import Holiday

from core.validators import (
    validate_non_empty_string,
    validate_trimmed_string,
)

class HolidaySerializer(
    serializers.ModelSerializer,
):
    """
    Serializer for the Holiday model.

    Used for:
    - Creating holidays
    - Updating holidays
    - Retrieving holiday details
    - Listing holidays
    """

    class Meta:

        model = Holiday

        fields = (
            "id",
            "company",
            "name",
            "date",
            "holiday_type",
            "description",
            "is_optional",
            "is_recurring",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

        validators = []

    # ======================================================
    # FIELD VALIDATION
    # ======================================================

    def validate_name(
        self,
        value,
    ):
        return validate_non_empty_string(
            value,
            "Holiday name",
        )

    def validate_description(
        self,
        value,
    ):
        return validate_trimmed_string(
            value,
        )

    # ======================================================
    # OBJECT VALIDATION
    # ======================================================

    def validate(
        self,
        attrs,
    ):
        """
        Validate company ownership,
        immutable company,
        and duplicate holidays.
        """

        request = self.context.get(
            "request",
        )

        company = attrs.get(
            "company",
            getattr(
                self.instance,
                "company",
                None,
            ),
        )

        holiday_date = attrs.get(
            "date",
            getattr(
                self.instance,
                "date",
                None,
            ),
        )

        # ------------------------------------------
        # Company Isolation
        # ------------------------------------------

        if (
            request
            and not request.user.is_superuser
            and company != request.user.company
        ):
            raise serializers.ValidationError(
                {
                    "company":
                    (
                        "You can only manage holidays "
                        "for your own company."
                    )
                }
            )

        # ------------------------------------------
        # Immutable Company
        # ------------------------------------------

        if (
            self.instance
            and "company" in attrs
            and attrs["company"] != self.instance.company
        ):
            raise serializers.ValidationError(
                {
                    "company":
                    (
                        "Company cannot be modified "
                        "after creation."
                    )
                }
            )

        # ------------------------------------------
        # Duplicate Holiday
        # ------------------------------------------

        queryset = Holiday.objects.filter(
            company=company,
            date=holiday_date,
        )

        if self.instance:

            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():

            raise serializers.ValidationError(
                {
                    "date":
                    (
                        "A holiday already exists "
                        "for this company on this date."
                    )
                }
            )

        return attrs