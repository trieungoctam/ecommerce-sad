from rest_framework import serializers
from .models import PaymentMethod, Transaction, PaymentGatewayConfig

class PaymentMethodSerializer(serializers.ModelSerializer):
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'payment_type', 'payment_type_display', 'provider',
            'account_number', 'expiry_date', 'is_default', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'account_number': {'write_only': True}
        }

    def validate(self, data):
        if data.get('payment_type') in ['CREDIT_CARD', 'DEBIT_CARD']:
            if not data.get('expiry_date'):
                raise serializers.ValidationError(
                    {"expiry_date": "Expiry date is required for card payments"}
                )
        return data

class TransactionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_details = PaymentMethodSerializer(source='payment_method', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'payment_method', 'payment_method_details',
            'order_id', 'amount', 'currency', 'status', 'status_display',
            'transaction_id', 'error_message', 'refund_amount',
            'created_at', 'updated_at', 'is_successful', 'is_refundable'
        ]
        read_only_fields = [
            'transaction_id', 'status', 'error_message', 'refund_amount',
            'created_at', 'updated_at', 'is_successful', 'is_refundable'
        ]

class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    gateway_display = serializers.CharField(source='get_gateway_display', read_only=True)

    class Meta:
        model = PaymentGatewayConfig
        fields = [
            'id', 'gateway', 'gateway_display', 'is_active',
            'config', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'config': {'write_only': True}  # Hide sensitive config data
        }