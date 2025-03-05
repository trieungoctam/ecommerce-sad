from django.db import models
from django.conf import settings
from decimal import Decimal

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('DIGITAL_WALLET', 'Digital Wallet'),
        ('COD', 'Cash on Delivery')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    provider = models.CharField(max_length=50)  # Visa, Mastercard, PayPal, etc.
    account_number = models.CharField(max_length=255)  # Encrypted card/account number
    expiry_date = models.DateField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_methods'
        unique_together = ['user', 'payment_type', 'account_number']

    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.provider} (*{self.account_number[-4:]})"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other payment methods of this user to non-default
            PaymentMethod.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    order_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=255, unique=True, null=True)
    gateway_response = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction {self.order_id} - {self.status}"

    @property
    def is_successful(self):
        return self.status == 'COMPLETED'

    @property
    def is_refundable(self):
        return self.status == 'COMPLETED' and self.refund_amount < self.amount

    def process_refund(self, amount):
        if not self.is_refundable:
            raise ValueError("Transaction is not refundable")
        if amount > (self.amount - self.refund_amount):
            raise ValueError("Refund amount exceeds available amount")
        self.refund_amount += amount
        if self.refund_amount == self.amount:
            self.status = 'REFUNDED'
        self.save()

class PaymentGatewayConfig(models.Model):
    GATEWAY_CHOICES = [
        ('STRIPE', 'Stripe'),
        ('PAYPAL', 'PayPal'),
        ('SQUARE', 'Square'),
        ('RAZORPAY', 'Razorpay')
    ]

    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)
    config = models.JSONField()  # Stores API keys, webhook URLs, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_gateway_configs'

    def __str__(self):
        return f"{self.get_gateway_display()} - {'Active' if self.is_active else 'Inactive'}"
