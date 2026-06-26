from rest_framework.exceptions import ValidationError


class ImmutableFieldError(
    ValidationError,
):
    """
    Raised when attempting to modify
    an immutable field.
    """

    def __init__(
        self,
        field_name,
    ):
        super().__init__(
            {
                field_name:
                (
                    f'"{field_name}" cannot be modified '
                    "after creation."
                )
            }
        )


class CompanyIsolationError(
    ValidationError,
):
    """
    Raised when data belongs
    to another company.
    """

    def __init__(self):

        super().__init__(
            {
                "company":
                (
                    "Operation is not allowed "
                    "across companies."
                )
            }
        )