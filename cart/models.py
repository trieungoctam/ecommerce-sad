from django.db import models
from django.conf import settings

class Cart(models.Model):
    customer_id = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product_type = models.CharField(
        max_length=50,
        help_text="Loại sản phẩm (ví dụ: 'book', 'mobile', 'shoes', 'clothes')"
    )
    product_id = models.CharField(
        max_length=100,
        help_text="ID sản phẩm từ service tương ứng (có thể là ObjectId dạng chuỗi)"
    )
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Cart {self.cart.id}"
