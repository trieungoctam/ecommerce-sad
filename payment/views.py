from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import PaymentMethod, Transaction, PaymentGatewayConfig
from .serializers import PaymentMethodSerializer, TransactionSerializer
import uuid

# Create your views here.

class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        payment_method = self.get_object()
        payment_method.is_default = True
        payment_method.save()
        return Response({'status': 'Default payment method set.'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        payment_method = self.get_object()
        payment_method.is_active = False
        payment_method.save()
        return Response({'status': 'Payment method deactivated.'})

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Add order_id and user to the request data
        data = request.data.copy()
        data['order_id'] = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        data['user'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Process payment through payment gateway
        try:
            transaction = self._process_payment(serializer.validated_data)
            return Response(
                TransactionSerializer(transaction).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _process_payment(self, validated_data):
        # Create transaction with pending status
        transaction = Transaction.objects.create(
            **validated_data,
            status='PENDING'
        )

        try:
            # Here you would integrate with your payment gateway
            # For example, Stripe, PayPal, etc.
            # This is a placeholder for the actual payment processing
            payment_successful = True  # Replace with actual payment processing

            if payment_successful:
                transaction.status = 'COMPLETED'
                transaction.transaction_id = f"TXN-{uuid.uuid4().hex[:16].upper()}"
            else:
                transaction.status = 'FAILED'
                transaction.error_message = "Payment processing failed"

            transaction.save()
            return transaction

        except Exception as e:
            transaction.status = 'FAILED'
            transaction.error_message = str(e)
            transaction.save()
            raise

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        transaction = self.get_object()
        amount = request.data.get('amount')

        if not amount:
            return Response(
                {'error': 'Refund amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            transaction.process_refund(amount)
            return Response(TransactionSerializer(transaction).data)
        except (ValueError, TypeError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        transaction = self.get_object()
        if transaction.status not in ['PENDING', 'PROCESSING']:
            return Response(
                {'error': 'Only pending or processing transactions can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction.status = 'CANCELLED'
        transaction.save()
        return Response(TransactionSerializer(transaction).data)
