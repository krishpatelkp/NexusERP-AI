from django.urls import path

from .views import (
    PayrollCycleCreateAPIView,
    PayrollCycleListAPIView,
    PayrollCycleDetailAPIView,
    PayrollCycleActivateAPIView,

    PayrollRunCreateAPIView,
    PayrollRunListAPIView,
    PayrollRunDetailAPIView,
    PayrollRunProcessAPIView,
    PayrollRunApproveAPIView,
    PayrollRunFinalizeAPIView,
    PayrollRunCancelAPIView,

    PayrollItemListAPIView,
    PayslipListAPIView,
    MyPayslipListAPIView,
)

urlpatterns = [

    # ======================================================
    # PAYROLL CYCLE
    # ======================================================

    path(
        "cycles/",
        PayrollCycleCreateAPIView.as_view(),
        name="payroll-cycle-create",
    ),

    path(
        "cycles/list/",
        PayrollCycleListAPIView.as_view(),
        name="payroll-cycle-list",
    ),

    path(
        "cycles/<int:pk>/",
        PayrollCycleDetailAPIView.as_view(),
        name="payroll-cycle-detail",
    ),

    path(
        "cycles/<int:pk>/activate/",
        PayrollCycleActivateAPIView.as_view(),
        name="payroll-cycle-activate",
    ),

    # ======================================================
    # PAYROLL RUN
    # ======================================================

    path(
        "cycles/<int:pk>/runs/",
        PayrollRunCreateAPIView.as_view(),
        name="payroll-run-create",
    ),

    path(
        "cycles/<int:pk>/runs/list/",
        PayrollRunListAPIView.as_view(),
        name="payroll-run-list",
    ),

    path(
        "runs/<int:pk>/",
        PayrollRunDetailAPIView.as_view(),
        name="payroll-run-detail",
    ),

    path(
        "runs/<int:pk>/process/",
        PayrollRunProcessAPIView.as_view(),
        name="payroll-run-process",
    ),

    path(
        "runs/<int:pk>/approve/",
        PayrollRunApproveAPIView.as_view(),
        name="payroll-run-approve",
    ),

    path(
        "runs/<int:pk>/finalize/",
        PayrollRunFinalizeAPIView.as_view(),
        name="payroll-run-finalize",
    ),

    path(
        "runs/<int:pk>/cancel/",
        PayrollRunCancelAPIView.as_view(),
        name="payroll-run-cancel",
    ),

    # ======================================================
    # PAYROLL ITEMS
    # ======================================================

    path(
        "runs/<int:pk>/items/",
        PayrollItemListAPIView.as_view(),
        name="payroll-item-list",
    ),

    # ======================================================
    # PAYSLIPS
    # ======================================================

    path(
        "runs/<int:pk>/payslips/",
        PayslipListAPIView.as_view(),
        name="payslip-list",
    ),

    path(
        "my-payslips/",
        MyPayslipListAPIView.as_view(),
        name="my-payslips",
    ),
]