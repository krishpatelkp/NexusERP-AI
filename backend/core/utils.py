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


def get_user_company(user):
    """
    Safely retrieves the company instance associated with a user or request.
    Handles:
    - User with direct `company` foreign key (admin, HR, regular user)
    - User with reverse `employee_profile.company` relation
    - Fallback for superusers if needed (e.g. first company in DB)
    - None if unauthenticated or no company found
    """
    if not user or not getattr(user, "is_authenticated", False):
        return None
    company = getattr(user, "company", None)
    if company:
        return company
    emp_profile = getattr(user, "employee_profile", None)
    if emp_profile and getattr(emp_profile, "company", None):
        return emp_profile.company
    if getattr(user, "is_superuser", False):
        from company.models import Company
        return Company.objects.first()
    return None