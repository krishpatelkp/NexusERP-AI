from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# ─────────────────────────────────────────
# SWAGGER / API DOCUMENTATION SETUP
# ─────────────────────────────────────────

schema_view = get_schema_view(
    openapi.Info(
        title="NexusERP AI API",
        default_version="v1",
        description="API documentation for NexusERP AI – Enterprise Workflow Automation Platform",
        contact=openapi.Contact(email="admin@nexuserp.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


# ─────────────────────────────────────────
# URL PATTERNS
# ─────────────────────────────────────────

urlpatterns = [

    # Django Admin
    path(
        "admin/",
        admin.site.urls,
    ),

    # Authentication APIs
    path(
        "api/auth/",
        include("accounts.urls"),
    ),

    # Swagger UI
    path(
        "api/docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),

    # ReDoc (alternative API docs)
    path(
        "api/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),

    path("api/employees/", include("employees.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)