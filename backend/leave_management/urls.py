from django.urls import path

from .views import (
    LeaveRequestCreateAPIView,
    LeaveRequestListAPIView,
    LeaveRequestRetrieveAPIView,
    ApproveLeaveAPIView,
    RejectLeaveAPIView,
    CancelLeaveAPIView,
    LeaveTypeListAPIView,
    LeaveBalanceListAPIView,
)


urlpatterns = [

    # ======================================================
    # LEAVE TYPES & BALANCES
    # ======================================================

    path(
        "types/",
        LeaveTypeListAPIView.as_view(),
        name="leave_type_list",
    ),

    path(
        "balances/",
        LeaveBalanceListAPIView.as_view(),
        name="leave_balance_list",
    ),

    # ======================================================
    # LEAVE REQUESTS
    # ======================================================

    path(
        "requests/",
        LeaveRequestListAPIView.as_view(),
        name="leave_request_list",
    ),

    path(
        "requests/apply/",
        LeaveRequestCreateAPIView.as_view(),
        name="leave_request_apply",
    ),

    path(
        "requests/<int:pk>/",
        LeaveRequestRetrieveAPIView.as_view(),
        name="leave_request_detail",
    ),

    # ======================================================
    # APPROVAL WORKFLOW
    # ======================================================

    path(
        "requests/<int:pk>/approve/",
        ApproveLeaveAPIView.as_view(),
        name="leave_request_approve",
    ),

    path(
        "requests/<int:pk>/reject/",
        RejectLeaveAPIView.as_view(),
        name="leave_request_reject",
    ),

    path(
        "requests/<int:pk>/cancel/",
        CancelLeaveAPIView.as_view(),
        name="leave_request_cancel",
    ),
]