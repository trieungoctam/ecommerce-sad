from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from book.models import Book
from mongoengine.errors import DoesNotExist

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shopping carts.
    Provides CRUD operations and custom actions for cart management.
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all carts for staff users, but only own carts for regular users."""
        if self.request.user.is_staff:
            return Cart.objects.all()
        return Cart.objects.filter(user=self.request.user)

    def get_active_cart(self):
        """Get or create an active cart for the current user."""
        cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        if not cart:
            cart = Cart.objects.create(user=self.request.user)
        return cart

    def check_product_availability(self, product_type, product_id, quantity):
        """Check if product exists and has sufficient stock."""
        try:
            if product_type == 'book':
                product = Book.objects.get(id=product_id)
                if product.stock < quantity:
                    raise ValidationError(f"Insufficient stock. Available: {product.stock}")
                return product
            # Add other product types here (mobile, shoes)
            raise ValidationError(f"Invalid product type: {product_type}")
        except DoesNotExist:
            raise ValidationError(f"Product not found: {product_id}")

    @transaction.atomic
    def perform_create(self, serializer):
        """Create a new cart only if user has no active cart."""
        existing_cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        if existing_cart:
            raise ValidationError("User already has an active cart")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the current user's active cart."""
        cart = self.get_active_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def add_item(self, request, pk=None):
        """Add an item to the cart with stock validation."""
        cart = self.get_object()
        if not cart.is_active:
            return Response(
                {"error": "Cannot modify an inactive cart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_type = serializer.validated_data['product_type']
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)

        try:
            # Validate product and stock
            product = self.check_product_availability(product_type, product_id, quantity)

            # Check if item already exists in cart
            try:
                item = cart.items.get(product_type=product_type, product_id=product_id)
                new_quantity = item.quantity + quantity
                if new_quantity > product.stock:
                    raise ValidationError(
                        f"Cannot add {quantity} more items. Available stock: {product.stock}"
                    )
                item.quantity = new_quantity
                item.save()
            except CartItem.DoesNotExist:
                serializer.save(cart=cart, price=product.price)

            return Response(CartSerializer(cart).data)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def remove_item(self, request, pk=None):
        """Remove an item from the cart."""
        cart = self.get_object()
        if not cart.is_active:
            return Response(
                {"error": "Cannot modify an inactive cart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item_id = request.data.get('item_id')
        if not item_id:
            return Response(
                {"error": "item_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = cart.items.get(id=item_id)
            item.delete()
            return Response(CartSerializer(cart).data)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def update_quantity(self, request, pk=None):
        """Update item quantity with stock validation."""
        cart = self.get_object()
        if not cart.is_active:
            return Response(
                {"error": "Cannot modify an inactive cart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)

        if not item_id:
            return Response(
                {"error": "item_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {"error": "Quantity must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = cart.items.get(id=item_id)
            # Validate stock
            product = self.check_product_availability(
                item.product_type,
                item.product_id,
                quantity
            )
            item.quantity = quantity
            item.save()
            return Response(CartSerializer(cart).data)

        except (CartItem.DoesNotExist, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def clear(self, request, pk=None):
        """Clear all items from the cart."""
        cart = self.get_object()
        if not cart.is_active:
            return Response(
                {"error": "Cannot modify an inactive cart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.items.all().delete()
        return Response(CartSerializer(cart).data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def checkout(self, request, pk=None):
        """Process checkout and validate stock availability."""
        cart = self.get_object()
        if not cart.is_active:
            return Response(
                {"error": "Cart is already checked out"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart.items.exists():
            return Response(
                {"error": "Cannot checkout empty cart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate stock for all items
            for item in cart.items.all():
                product = self.check_product_availability(
                    item.product_type,
                    item.product_id,
                    item.quantity
                )
                # Update stock (you might want to move this to an order processing service)
                if item.product_type == 'book':
                    product.stock -= item.quantity
                    product.save()

            # Deactivate current cart
            cart.is_active = False
            cart.save()

            # Create new active cart
            new_cart = Cart.objects.create(user=request.user)
            return Response({
                "message": "Checkout successful",
                "old_cart": CartSerializer(cart).data,
                "new_cart": CartSerializer(new_cart).data
            })

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
