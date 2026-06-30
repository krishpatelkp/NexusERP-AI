from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payroll.models import Payslip

from .models import Payment
from .serializers import (
    PaymentSerializer,
    CreatePaymentSerializer,
    MarkProcessingSerializer,
    MarkPaidSerializer,
    MarkFailedSerializer,
    CancelPaymentSerializer,
)
from .services import PaymentService


# ==========================================================
# CREATE PAYMENT
# ==========================================================

class PaymentCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreatePaymentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        payslip = get_object_or_404(
            Payslip,
            pk=serializer.validated_data["payslip"],
        )

        service = PaymentService(
            company=request.user.company,
        )

        payment = service.create_payment(
            payslip=payslip,
            payment_method=serializer.validated_data["payment_method"],
            processed_by=request.user,
            remarks=serializer.validated_data.get(
                "remarks",
                "",
            ),
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )
    

# ==========================================================
# PAYMENT LIST
# ==========================================================

class PaymentListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        payments = (
            Payment.objects
            .filter(
                company=request.user.company,
            )
            .order_by("-created_at")
        )

        serializer = PaymentSerializer(
            payments,
            many=True,
        )

        return Response(serializer.data)
    

# ==========================================================
# PAYMENT DETAIL
# ==========================================================

class PaymentDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(
        self,
        request,
        payment_id,
    ):

        payment = get_object_or_404(
            Payment,
            pk=payment_id,
            company=request.user.company,
        )

        serializer = PaymentSerializer(
            payment,
        )

        return Response(serializer.data)
    

# ==========================================================
# MARK PAYMENT AS PROCESSING
# ==========================================================

class PaymentMarkProcessingAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        payment_id,
    ):

        serializer = MarkProcessingSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        payment = get_object_or_404(
            Payment,
            pk=payment_id,
            company=request.user.company,
        )

        service = PaymentService(
            company=request.user.company,
        )

        payment = service.mark_processing(
            payment=payment,
            processed_by=request.user,
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# MARK PAYMENT AS PAID
# ==========================================================

class PaymentMarkPaidAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        payment_id,
    ):

        serializer = MarkPaidSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        payment = get_object_or_404(
            Payment,
            pk=payment_id,
            company=request.user.company,
        )

        service = PaymentService(
            company=request.user.company,
        )

        payment = service.mark_paid(
            payment=payment,
            payment_date=serializer.validated_data["payment_date"],
            payment_method=serializer.validated_data.get(
                "payment_method"
            ),
            transaction_id=serializer.validated_data.get(
                "transaction_id",
                "",
            ),
            bank_reference_number=serializer.validated_data.get(
                "bank_reference_number",
                "",
            ),
            remarks=serializer.validated_data.get(
                "remarks",
                "",
            ),
            processed_by=request.user,
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# MARK PAYMENT AS FAILED
# ==========================================================

class PaymentMarkFailedAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        payment_id,
    ):

        serializer = MarkFailedSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        payment = get_object_or_404(
            Payment,
            pk=payment_id,
            company=request.user.company,
        )

        service = PaymentService(
            company=request.user.company,
        )

        payment = service.mark_failed(
            payment=payment,
            failure_reason=serializer.validated_data["failure_reason"],
            remarks=serializer.validated_data.get(
                "remarks",
                "",
            ),
            processed_by=request.user,
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# CANCEL PAYMENT
# ==========================================================

class PaymentCancelAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        payment_id,
    ):

        serializer = CancelPaymentSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        payment = get_object_or_404(
            Payment,
            pk=payment_id,
            company=request.user.company,
        )

        service = PaymentService(
            company=request.user.company,
        )

        payment = service.cancel_payment(
            payment=payment,
            remarks=serializer.validated_data.get(
                "remarks",
                "",
            ),
            processed_by=request.user,
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )