from rest_framework import serializers


class ImmutableFieldsMixin:
    """
    Prevents modification of immutable fields after an object
    has been created.

    Usage:

        class EmployeeSerializer(
            ImmutableFieldsMixin,
            serializers.ModelSerializer,
        ):
            immutable_fields = (
                "company",
                "employee_id",
            )
    """

    immutable_fields = ()

    def validate(
        self,
        attrs,
    ):
        """
        Prevent updates to immutable fields.
        """

        attrs = super().validate(attrs)

        if not self.instance:
            return attrs

        for field in self.immutable_fields:

            if field not in attrs:
                continue

            old_value = getattr(
                self.instance,
                field,
            )

            new_value = attrs[field]

            if old_value != new_value:

                raise serializers.ValidationError(
                    {
                        field:
                        (
                            f'"{field}" cannot be modified '
                            "after creation."
                        )
                    }
                )

        return attrs