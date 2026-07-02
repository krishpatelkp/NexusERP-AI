from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Asset,
    AssetAssignment,
    AssetCategory,
    AssetMaintenance,
    Vendor,
)

from .serializers import (
    AssetCategorySerializer,
    VendorSerializer,
    AssetSerializer,
    AssetAssignmentSerializer,
    AssetMaintenanceSerializer,
    CreateAssetSerializer,
    AssignAssetSerializer,
    ReturnAssetSerializer,
    ScheduleMaintenanceSerializer,
    CompleteMaintenanceSerializer,
    RetireAssetSerializer,
)

from .services import InventoryService
from .pagination import InventoryPagination


# ==========================================================
# HELPER — convert DRF/Django ValidationError to 400
# ==========================================================

def _raise_drf(exc):
    """
    InventoryService raises rest_framework.exceptions
    .ValidationError directly (confirmed in services.py
    imports), so in most cases nothing needs converting.
    This helper exists only as a safety net in case a
    plain string or Django-style error reaches here.
    """
    if hasattr(exc, "detail"):
        raise exc
    raise DRFValidationError(detail=str(exc))


# ==========================================================
# ASSET CATEGORY — LIST
# ==========================================================

class AssetCategoryListAPIView(ListAPIView):
    """
    GET /api/inventory/categories/
    """

    serializer_class = AssetCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InventoryPagination

    def get_queryset(self):
        return (
            AssetCategory.objects
            .filter(
                company=self.request.user.employee_profile.company,
                is_active=True,
            )
            .order_by("name")
        )


# ==========================================================
# VENDOR — LIST
# ==========================================================

class VendorListAPIView(ListAPIView):
    """
    GET /api/inventory/vendors/
    """

    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InventoryPagination

    def get_queryset(self):
        return (
            Vendor.objects
            .filter(
                company=self.request.user.employee_profile.company,
                is_active=True,
            )
            .order_by("name")
        )


# ==========================================================
# ASSET — LIST
# ==========================================================

class AssetListAPIView(ListAPIView):
    """
    GET /api/inventory/assets/

    Supports optional filtering via query params:
        ?status=Available
        ?category=<id>
    """

    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InventoryPagination

    def get_queryset(self):

        queryset = (
            Asset.objects
            .filter(
                company=self.request.user.employee_profile.company,
                is_active=True,
            )
            .select_related("category", "vendor")
            .order_by("category", "asset_tag")
        )

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        category_param = self.request.query_params.get("category")
        if category_param:
            queryset = queryset.filter(category_id=category_param)

        return queryset


# ==========================================================
# ASSET — DETAIL
# ==========================================================

class AssetDetailAPIView(RetrieveAPIView):
    """
    GET /api/inventory/assets/<id>/
    """

    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Asset.objects.filter(
            company=self.request.user.employee_profile.company,
        )


# ==========================================================
# ASSET — CREATE
# ==========================================================

class CreateAssetAPIView(APIView):
    """
    POST /api/inventory/assets/create/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = CreateAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = InventoryService(company=request.user.employee_profile.company)

        try:
            asset = service.create_asset(
                category=data["category"],
                asset_tag=data["asset_tag"],
                name=data["name"],
                vendor=data.get("vendor"),
                serial_number=data.get("serial_number", ""),
                brand=data.get("brand", ""),
                model=data.get("model", ""),
                description=data.get("description", ""),
                purchase_date=data.get("purchase_date"),
                purchase_cost=data.get("purchase_cost"),
                warranty_expiry=data.get("warranty_expiry"),
                invoice_number=data.get("invoice_number", ""),
                condition=data.get("condition"),
                location=data.get("location", ""),
                notes=data.get("notes", ""),
            )
        except Exception as exc:
            _raise_drf(exc)

        return Response(
            AssetSerializer(asset).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# ASSET — ASSIGN
# ==========================================================

class AssignAssetAPIView(APIView):
    """
    POST /api/inventory/assets/<id>/assign/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):

        asset = get_object_or_404(
            Asset,
            pk=pk,
            company=request.user.employee_profile.company,
        )

        serializer = AssignAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = InventoryService(company=request.user.employee_profile.company)

        try:
            assignment = service.assign_asset(
                asset=asset,
                employee=data["employee"],
                assigned_date=data.get("assigned_date"),
                assigned_condition=data.get("assigned_condition"),
                assigned_by=request.user,
                remarks=data.get("remarks", ""),
            )
        except Exception as exc:
            _raise_drf(exc)

        return Response(
            AssetAssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# ASSET — RETURN
# ==========================================================

class ReturnAssetAPIView(APIView):
    """
    POST /api/inventory/assets/<id>/return/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):

        asset = get_object_or_404(
            Asset,
            pk=pk,
            company=request.user.employee_profile.company,
        )

        serializer = ReturnAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = InventoryService(company=request.user.employee_profile.company)

        try:
            assignment = service.return_asset(
                asset=asset,
                returned_date=data.get("returned_date"),
                returned_condition=data.get("returned_condition"),
                received_by=request.user,
                remarks=data.get("remarks", ""),
            )
        except Exception as exc:
            _raise_drf(exc)

        return Response(
            AssetAssignmentSerializer(assignment).data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# MAINTENANCE — SCHEDULE
# ==========================================================

class ScheduleMaintenanceAPIView(APIView):
    """
    POST /api/inventory/assets/<id>/maintenance/schedule/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):

        asset = get_object_or_404(
            Asset,
            pk=pk,
            company=request.user.employee_profile.company,
        )

        serializer = ScheduleMaintenanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = InventoryService(company=request.user.employee_profile.company)

        try:
            maintenance = service.schedule_maintenance(
                asset=asset,
                maintenance_type=data["maintenance_type"],
                description=data["description"],
                scheduled_date=data.get("scheduled_date"),
                vendor=data.get("vendor"),
                cost=data.get("cost"),
                outcome_notes=data.get("outcome_notes", ""),
                reported_by=request.user,
            )
        except Exception as exc:
            _raise_drf(exc)

        return Response(
            AssetMaintenanceSerializer(maintenance).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# MAINTENANCE — COMPLETE
# ==========================================================

class CompleteMaintenanceAPIView(APIView):
    """
    POST /api/inventory/maintenance/<id>/complete/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):

        maintenance = get_object_or_404(
            AssetMaintenance,
            pk=pk,
            company=request.user.employee_profile.company,
        )

        serializer = CompleteMaintenanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = InventoryService(company=request.user.employee_profile.company)

        try:
            maintenance = service.complete_maintenance(
                maintenance=maintenance,
                completed_date=data.get("completed_date"),
                asset_status=data.get("asset_status"),
                asset_condition=data.get("asset_condition"),
                outcome_notes=data.get("outcome_notes", ""),
            )
        except Exception as exc:
            _raise_drf(exc)

        return Response(
            AssetMaintenanceSerializer(maintenance).data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ASSET — RETIRE
# ==========================================================

class RetireAssetAPIView(APIView):
    """
    POST /api/inventory/assets/<id>/retire/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):

        asset = get_object_or_404(
            Asset,
            pk=pk,
            company=request.user.employee_profile.company,
        )

        serializer = RetireAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = InventoryService(company=request.user.employee_profile.company)

        try:
            asset = service.retire_asset(
                asset=asset,
                notes=data.get("notes", ""),
            )
        except Exception as exc:
            _raise_drf(exc)

        return Response(
            AssetSerializer(asset).data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ASSET ASSIGNMENT — HISTORY LIST
# ==========================================================

class AssetAssignmentListAPIView(ListAPIView):
    """
    GET /api/inventory/assignments/

    Supports optional filtering:
        ?asset=<id>
        ?employee=<id>
        ?active=true   (currently held, not yet returned)
    """

    serializer_class = AssetAssignmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InventoryPagination

    def get_queryset(self):

        queryset = (
            AssetAssignment.objects
            .filter(company=self.request.user.employee_profile.company)
            .select_related("asset", "employee")
            .order_by("-assigned_date")
        )

        asset_param = self.request.query_params.get("asset")
        if asset_param:
            queryset = queryset.filter(asset_id=asset_param)

        employee_param = self.request.query_params.get("employee")
        if employee_param:
            queryset = queryset.filter(employee_id=employee_param)

        active_param = self.request.query_params.get("active")
        if active_param == "true":
            queryset = queryset.filter(returned_date__isnull=True)

        return queryset


# ==========================================================
# ASSET MAINTENANCE — HISTORY LIST
# ==========================================================

class AssetMaintenanceListAPIView(ListAPIView):
    """
    GET /api/inventory/maintenance/

    Supports optional filtering:
        ?asset=<id>
        ?status=Scheduled
    """

    serializer_class = AssetMaintenanceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InventoryPagination

    def get_queryset(self):

        queryset = (
            AssetMaintenance.objects
            .filter(company=self.request.user.employee_profile.company)
            .select_related("asset", "vendor")
            .order_by("-scheduled_date")
        )

        asset_param = self.request.query_params.get("asset")
        if asset_param:
            queryset = queryset.filter(asset_id=asset_param)

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset