"""
==========================================================
NexusERP-AI  |  data_exchange  |  views.py
==========================================================

API endpoints for Data Exchange Framework.

Responsibilities:
  - Validate requests via Serializers
  - Call Services for business logic
  - Return structured JSON responses or file downloads
  - Handle exceptions gracefully
==========================================================
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse

from .serializers import (
    ImportPreviewRequestSerializer,
    ImportConfirmRequestSerializer,
    ExportRequestSerializer,
    ImportLogSerializer,
)
from .services import get_import_service, ImportCancelService
from .templates import ImportTemplateGenerator
from .exporters import get_exporter
from .exceptions import DataExchangeError
from .constants import ImportModule
from .models import ImportLog


class ImportPreviewAPIView(APIView):
    """
    Phase 1: Upload file, read, validate, and return preview.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    # We must explicitly accept multipart/form-data
    from rest_framework.parsers import MultiPartParser, FormParser
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ImportPreviewRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        module = serializer.validated_data["module"]
        file = serializer.validated_data["file"]

        try:
            service = get_import_service(module, request.user.company, request.user)
            result = service.preview(file)
            return Response(result, status=status.HTTP_200_OK)
        except DataExchangeError as e:
            return Response({"error": e.message, "details": e.to_dict()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImportConfirmAPIView(APIView):
    """
    Phase 2: Confirm import based on log ID.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ImportConfirmRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        log_id = serializer.validated_data["log_id"]

        try:
            # Re-fetch the module from the log to instatiate the right service
            log = ImportLog.objects.get(id=log_id, company=request.user.company)
            service = get_import_service(log.module, request.user.company, request.user)
            result = service.confirm(log_id)
            return Response(result, status=status.HTTP_200_OK)
        except ImportLog.DoesNotExist:
            return Response({"error": "Import log not found."}, status=status.HTTP_404_NOT_FOUND)
        except DataExchangeError as e:
            return Response({"error": e.message, "details": e.to_dict()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImportCancelAPIView(APIView):
    """
    Cancel an import in PREVIEW state.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, log_id, *args, **kwargs):
        try:
            service = ImportCancelService(request.user.company, request.user)
            result = service.cancel(log_id)
            return Response(result, status=status.HTTP_200_OK)
        except DataExchangeError as e:
            return Response({"error": e.message, "details": e.to_dict()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadTemplateAPIView(APIView):
    """
    Download empty template for a module.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, module, *args, **kwargs):
        if module not in ImportModule.ALL:
            return Response({"error": "Invalid module."}, status=status.HTTP_400_BAD_REQUEST)

        generator = ImportTemplateGenerator(module)
        buffer = generator.generate()

        response = HttpResponse(
            buffer,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{generator.filename}"'
        return response


class ImportHistoryAPIView(APIView):
    """
    View import history.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logs = ImportLog.objects.filter(company=request.user.company).order_by("-started_at")[:50]
        serializer = ImportLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportAPIView(APIView):
    """
    Generate and download export.
    Note: For production, large exports should be async via Celery.
    Here we return it synchronously.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = ExportRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        module = serializer.validated_data["module"]
        export_format = serializer.validated_data["format"]

        # 1. Get data by reusing report services (which are already company-isolated)
        data = self._get_export_data(module, request)
        if isinstance(data, Response):  # Handle errors returned from report services
            return data

        columns = self._get_export_columns(module)

        # 2. Export
        try:
            exporter = get_exporter(export_format)
            buffer = exporter.generate(data=data, columns=columns, title=module.title())
            
            response = HttpResponse(buffer, content_type=exporter.content_type)
            filename = f"export_{module}_{datetime.now().strftime('%Y%m%d%H%M')}{exporter.extension}"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            
            # Log it
            from .models import ExportLog
            from .constants import ExportStatus
            ExportLog.objects.create(
                company=request.user.company,
                exported_by=request.user,
                module=module,
                export_format=export_format,
                status=ExportStatus.COMPLETED,
                total_rows=len(data)
            )
            
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_export_data(self, module, request):
        """Fetch data by calling the respective report service."""
        from .constants import ExportModule
        
        # We construct a fake request context if needed, or pass kwargs.
        # It's better to call the report service directly.
        # Since report services are meant to return QuerySets or structured dicts,
        # we serialize them dynamically.
        
        if module == ExportModule.EMPLOYEES:
            from employees.models import Employee
            qs = Employee.objects.filter(company=request.user.company).select_related('department', 'designation')
            return [
                {
                    "employee_id": e.employee_id,
                    "first_name": e.first_name,
                    "last_name": e.last_name,
                    "email": e.email,
                    "department": e.department.department_name if e.department else "",
                    "designation": e.designation.designation_name if e.designation else "",
                    "status": e.employee_status,
                } for e in qs
            ]
        
        elif module == ExportModule.ATTENDANCE:
            from attendance.models import Attendance
            from datetime import date
            month = request.query_params.get("month", date.today().month)
            year = request.query_params.get("year", date.today().year)
            qs = Attendance.objects.filter(employee__company=request.user.company, date__month=month, date__year=year).select_related("employee")
            return [
                {
                    "employee_id": a.employee.employee_id,
                    "name": a.employee.full_name,
                    "date": a.date,
                    "status": a.status,
                    "check_in": a.check_in.strftime("%H:%M") if a.check_in else "",
                    "check_out": a.check_out.strftime("%H:%M") if a.check_out else "",
                } for a in qs
            ]
            
        elif module == ExportModule.INVENTORY:
            from inventory.models import Asset
            qs = Asset.objects.filter(company=request.user.company).select_related('category')
            return [
                {
                    "asset_tag": a.asset_tag,
                    "name": a.name,
                    "category": a.category.name if a.category else "",
                    "status": a.status,
                    "condition": a.condition,
                } for a in qs
            ]
            
        # Add others as needed
        return []

    def _get_export_columns(self, module):
        from .constants import ExportModule
        if module == ExportModule.EMPLOYEES:
            return ["employee_id", "first_name", "last_name", "email", "department", "designation", "status"]
        if module == ExportModule.ATTENDANCE:
            return ["employee_id", "name", "date", "status", "check_in", "check_out"]
        if module == ExportModule.INVENTORY:
            return ["asset_tag", "name", "category", "status", "condition"]
        return []

from datetime import datetime
