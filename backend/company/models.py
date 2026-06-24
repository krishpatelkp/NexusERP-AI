from django.db import models

# Create your models here.

class Company(models.Model):
    company_name = models.CharField(
        max_length=255,
        unique=True
    )

    company_code = models.CharField(
        max_length=20,
        unique=True
    )

    email = models.EmailField(
        unique=True
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True
    )

    website = models.URLField(
        blank=True
    )

    gst_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True
    )

    pan_number = models.CharField(
        max_length=10,
        unique=True,
        blank=True
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    country = models.CharField(
        max_length=100,
        default="India"
    )

    postal_code = models.CharField(
        max_length=20
    )

    industry = models.CharField(
        max_length=100,
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

    def __str__(self):
        return self.company_name
    

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["company_name"]