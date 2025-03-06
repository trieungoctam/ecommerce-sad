from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    Used for read operations and basic cart item manipulations.
    """
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product_type', 'product_id', 'product_name',
                  'quantity', 'price', 'added_at']
        read_only_fields = ['id', 'added_at']

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart model with nested items.
    Used for read operations and displaying cart details.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'created', 'items', 'total_price', 'item_count']
        read_only_fields = ['id', 'created', 'total_price', 'item_count']

    def get_total_price(self, obj):
        """Calculate the total price of all items in the cart"""
        return sum(item.price * item.quantity for item in obj.items.all())

    def get_item_count(self, obj):
        """Calculate the total number of items in the cart"""
        return sum(item.quantity for item in obj.items.all())

class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used specifically for creating cart items.
    Does not require product_name and price as they will be fetched from the product service.
    """
    class Meta:
        model = CartItem
        fields = ['product_type', 'product_id', 'quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value

class CartCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a cart with multiple items.
    Not directly tied to a model, handles the complex create operation.
    """
    customer_id = serializers.CharField(required=True)
    items = CartItemCreateSerializer(many=True, required=False)

    def validate_customer_id(self, value):
        if not value:
            raise serializers.ValidationError("Customer ID is required")
        return value