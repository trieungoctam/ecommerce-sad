from django.db import models
from django.conf import settings
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'carts'
        ordering = ['-created_at']

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Cart {self.id} - {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product_type = models.CharField(max_length=50)  # 'book', 'mobile', 'shoes'
    product_id = models.CharField(max_length=100)  # MongoDB ObjectId or other ID
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        ordering = ['-added_at']
        unique_together = ('cart', 'product_type', 'product_id')

    @property
    def total_price(self):
        return Decimal(str(self.price)) * self.quantity

    def __str__(self):
        return f"{self.product_type} - {self.product_id} ({self.quantity})"
