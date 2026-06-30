from django.urls import path

from .views import (
    AssetAssignmentListAPIView,
    AssetCategoryListAPIView,
    AssetDetailAPIView,
    AssetListAPIView,
    AssetMaintenanceListAPIView,
    AssignAssetAPIView,
    CompleteMaintenanceAPIView,
    CreateAssetAPIView,
    RetireAssetAPIView,
    ReturnAssetAPIView,
    ScheduleMaintenanceAPIView,
    VendorListAPIView,
)

urlpatterns = [

    # ======================================================
    # ASSET CATEGORIES
    # ======================================================

    path(
        "categories/",
        AssetCategoryListAPIView.as_view(),
        name="asset-category-list",
    ),

    # ======================================================
    # VENDORS
    # ======================================================

    path(
        "vendors/",
        VendorListAPIView.as_view(),
        name="vendor-list",
    ),

    # ======================================================
    # ASSETS
    # ======================================================

    path(
        "assets/",
        AssetListAPIView.as_view(),
        name="asset-list",
    ),

    path(
        "assets/<int:pk>/",
        AssetDetailAPIView.as_view(),
        name="asset-detail",
    ),

    path(
        "assets/create/",
        CreateAssetAPIView.as_view(),
        name="asset-create",
    ),

    path(
        "assets/<int:pk>/assign/",
        AssignAssetAPIView.as_view(),
        name="asset-assign",
    ),

    path(
        "assets/<int:pk>/return/",
        ReturnAssetAPIView.as_view(),
        name="asset-return",
    ),

    path(
        "assets/<int:pk>/retire/",
        RetireAssetAPIView.as_view(),
        name="asset-retire",
    ),

    # ======================================================
    # MAINTENANCE
    # ======================================================

    path(
        "assets/<int:pk>/maintenance/schedule/",
        ScheduleMaintenanceAPIView.as_view(),
        name="maintenance-schedule",
    ),

    path(
        "maintenance/<int:pk>/complete/",
        CompleteMaintenanceAPIView.as_view(),
        name="maintenance-complete",
    ),

    path(
        "maintenance/",
        AssetMaintenanceListAPIView.as_view(),
        name="maintenance-list",
    ),

    # ======================================================
    # ASSIGNMENTS
    # ======================================================

    path(
        "assignments/",
        AssetAssignmentListAPIView.as_view(),
        name="assignment-list",
    ),
]