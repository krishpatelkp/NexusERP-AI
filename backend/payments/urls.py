from django.urls import path

from .views import (
    PaymentCreateAPIView,
    PaymentListAPIView,
    PaymentDetailAPIView,
    PaymentMarkProcessingAPIView,
    PaymentMarkPaidAPIView,
    PaymentMarkFailedAPIView,
    PaymentCancelAPIView,
)

urlpatterns = [

    path(
        "",
        PaymentListAPIView.as_view(),
        name="payment-list",
    ),

    path(
        "create/",
        PaymentCreateAPIView.as_view(),
        name="payment-create",
    ),

    path(
        "<int:payment_id>/",
        PaymentDetailAPIView.as_view(),
        name="payment-detail",
    ),
    path(
        "<int:payment_id>/processing/",
        PaymentMarkProcessingAPIView.as_view(),
        name="payment-mark-processing",
    ),
    path(
        "<int:payment_id>/paid/",
        PaymentMarkPaidAPIView.as_view(),
        name="payment-mark-paid",
    ),
    path(
        "<int:payment_id>/failed/",
        PaymentMarkFailedAPIView.as_view(),
        name="payment-mark-failed",
    ),

    path(
        "<int:payment_id>/cancel/",
        PaymentCancelAPIView.as_view(),
        name="payment-cancel",
    ),
]
