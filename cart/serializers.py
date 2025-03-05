from rest_framework import serializers
from .models import Cart, CartItem
from book.models import Book
from mongoengine.errors import DoesNotExist

class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product_type', 'product_id', 'quantity', 'price',
                 'total_price', 'product_name', 'added_at', 'updated_at']
        read_only_fields = ['price', 'added_at', 'updated_at']

    def get_product_name(self, obj):
        try:
            if obj.product_type == 'book':
                book = Book.objects.get(id=obj.product_id)
                return book.title
            # Add other product types here (mobile, shoes)
            return ''
        except DoesNotExist:
            return 'Product not found'

    def validate(self, data):
        product_type = data.get('product_type')
        product_id = data.get('product_id')

        # Validate product exists and get its price
        try:
            if product_type == 'book':
                product = Book.objects.get(id=product_id)
                data['price'] = product.price
            # Add validation for other product types
            else:
                raise serializers.ValidationError(f"Invalid product type: {product_type}")
        except DoesNotExist:
            raise serializers.ValidationError(f"Product not found: {product_id}")

        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['user', 'created_at', 'updated_at']