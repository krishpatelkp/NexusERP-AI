from django.contrib import admin
from .models import Company

# Register your models here.
@admin.register(Company)  #Register the Company model using the custom Admin class
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "company_code",
        "email",
        "city",
        "is_active",
    )
    
    search_fields = (
        "company_name",
        "company_code",
        "email",
    )

    list_filter = (
        "is_active",
        "city",
    )

    ordering = (
        "company_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )