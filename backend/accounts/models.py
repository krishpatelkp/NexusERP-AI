from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError

from company.models import Company
from .managers import CustomUserManager


class Role(models.Model):
    """
    Stores all roles available within a company.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="roles"
    )

    role_name = models.CharField(
        max_length=100
    )

    role_code = models.CharField(
        max_length=30
    )

    description = models.TextField(
        blank=True
    )

    permissions = models.ManyToManyField(
        "Permission",
        through="RolePermission",
        related_name="roles",
        blank=True,
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "role_name"],
                name="unique_role_name_per_company",
            ),
            models.UniqueConstraint(
                fields=["company", "role_code"],
                name="unique_role_code_per_company",
            ),
        ]

    def save(self, *args, **kwargs):
         if self.role_code:
            self.role_code = (
                self.role_code.strip().upper()
            )
    
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.company_name} - {self.role_name}"


class Permission(models.Model):
    """
    Stores all permissions available in the ERP.
    """

    permission_name = models.CharField(
        max_length=100
    )

    permission_code = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "permission_code",
        ]

    def save(self, *args, **kwargs):
        if self.permission_code:
            self.permission_code = (
                self.permission_code.strip().lower()
            )
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.permission_name} ({self.permission_code})"
    

class RolePermission(models.Model):
    """
    Maps roles to permissions.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "role",
            "permission",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_role_permission",
            )
        ]

    def __str__(self):
        return (
            f"{self.role.role_name} -> "
            f"{self.permission.permission_code}"
        )



class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model used for authentication.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )

    email = models.EmailField(
        unique=True
    )

    username = models.CharField(
        max_length=100,
        unique=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def clean(self):
        """
        Require company and role for normal users.
        Allow Django superusers to exist without them.
        """
        super().clean()

        if not self.is_superuser:

            if self.company is None:
                raise ValidationError(
                    {"company": "Company is required."}
                )

            if self.role is None:
                raise ValidationError(
                    {"role": "Role is required."}
                )
            
    def has_perm_code(self, permission_code):
        """
        Return True if the user has the specified
        business permission through their assigned role.

        Examples:
            user.has_permission("employee.create")
            user.has_permission("employee.view")
            user.has_permission("leave.approve")
        """

        if not self.is_active:
            return False

        if self.is_superuser:
            return True

        if self.role is None:
            return False
        if not self.role.is_active:
            return False
        if not permission_code:
            return False

        permission_code = permission_code.strip().lower()

        return self.role.role_permissions.filter(
            permission__permission_code=permission_code,
            permission__is_active=True,
            is_active=True,
        ).exists()

    def __str__(self):
        return self.email