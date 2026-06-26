def normalize_email(
    email,
):
    return email.strip().lower()


def normalize_uppercase(
    value,
):
    return value.strip().upper()


def normalize_string(
    value,
):
    return value.strip()