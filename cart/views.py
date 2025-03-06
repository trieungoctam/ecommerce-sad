from rest_framework import generics, status
from rest_framework.response import Response
import requests
import json
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    CartCreateSerializer,
    CartItemCreateSerializer
)

# Service URLs - ideally these would be in settings.py
PRODUCT_SERVICE_URLS = getattr(settings, 'PRODUCT_SERVICE_URLS', {
    'book': 'http://127.0.0.1:9191/api/books',
})
CUSTOMER_SERVICE_URL = getattr(settings, 'CUSTOMER_SERVICE_URL',
                              "http://127.0.0.1:9191/api/customer/")

class CartCreateView(generics.CreateAPIView):
    """
    Create a new cart with optional items.
    Fetches customer and product data from their respective services.
    """
    serializer_class = CartCreateSerializer

    def fetch_customer_data(self, customer_id):
        """Fetch customer data from customer service"""
        url = f"{CUSTOMER_SERVICE_URL}{customer_id}/"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json(), None
            return None, f"Customer service error: {response.status_code}"
        except requests.RequestException as e:
            return None, f"Customer service unavailable: {str(e)}"

    def fetch_product_data(self, product_type, product_id):
        """Fetch product data from product service"""
        base_url = PRODUCT_SERVICE_URLS.get(product_type.lower())
        if not base_url:
            return None, f"Unsupported product type: {product_type}"

        url = f"{base_url}/detail/{product_id}/"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json(), None
            return None, f"Product service error: {response.status_code}"
        except requests.RequestException as e:
            return None, f"Product service unavailable: {str(e)}"

    def create(self, request, *args, **kwargs):
        request_data = request.data

        # Extract validated data
        customer_id = request_data.get('customer_id')
        items_data = request_data.get('items', [])

        # Step 1: Fetch customer data
        customer_data, error = self.fetch_customer_data(customer_id)
        if error:
            return Response(
                {"success": False, "message": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Create the cart
        cart = Cart.objects.create(customer_id=customer_id)

        print(cart)

        # Step 3: Process cart items
        processed_items = []
        failed_items = []

        for item in items_data:
            product_type = item['product_type']
            product_id = item['product_id']
            quantity = item['quantity']

            # Fetch product data
            product_data, error = self.fetch_product_data(product_type, product_id)
            if error:
                failed_items.append({
                    "item": item,
                    "reason": error
                })
                continue

            # Extract product details - adjust field names based on your API response
            product_name = product_data.get('title', product_data.get('name', 'Unknown'))
            price = product_data.get('price', 0)

            # Create cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product_type=product_type,
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                price=price
            )

            processed_items.append({
                "id": cart_item.id,
                "product_name": product_name,
                "quantity": quantity,
                "price": price
            })

        # Get the full cart data with serializer that includes items
        cart_serializer = CartSerializer(cart)

        # Prepare response
        response_data = {
            "success": True,
            "message": "Cart created successfully",
            "data": cart_serializer.data,
            "customer_data": customer_data
        }

        # Add failure information if any
        if failed_items:
            response_data["failed_items"] = failed_items

        return Response(response_data, status=status.HTTP_201_CREATED)

class CartListView(generics.ListAPIView):
    """
    List all carts, optionally filtered by customer_id.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset

class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a cart.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = 'id'

class CartItemListCreateView(generics.ListCreateAPIView):
    """
    List items in a cart or add a new item.
    """
    serializer_class = CartItemSerializer

    def get_queryset(self):
        """Filter cart items by cart_id from URL"""
        cart_id = self.kwargs.get('cart_id')
        return CartItem.objects.filter(cart_id=cart_id)

    def create(self, request, *args, **kwargs):
        cart_id = self.kwargs.get('cart_id')
        product_type = request.data.get('product_type')
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        # Validate input
        if not all([product_type, product_id]):
            return Response(
                {"detail": "Missing required fields: product_type, product_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify cart exists
        cart = get_object_or_404(Cart, id=cart_id)

        # Get product information from product service
        base_url = PRODUCT_SERVICE_URLS.get(product_type.lower())
        if not base_url:
            return Response(
                {"detail": f"Unsupported product type: {product_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        url = f"{base_url}/{product_id}/"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return Response(
                    {"detail": f"Product service error: {response.status_code}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            product_data = response.json()
        except requests.RequestException as e:
            return Response(
                {"detail": f"Product service unavailable: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract product details
        product_name = product_data.get('title', product_data.get('name', 'Unknown'))
        price = product_data.get('price', 0)

        # Check if product already exists in cart
        existing_item = CartItem.objects.filter(
            cart_id=cart_id,
            product_type=product_type,
            product_id=product_id
        ).first()

        if existing_item:
            # Update quantity if product already in cart
            existing_item.quantity += quantity
            existing_item.save()
            serializer = self.get_serializer(existing_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create new cart item
            cart_item_data = {
                'cart': cart_id,
                'product_type': product_type,
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity,
                'price': price
            }

            serializer = self.get_serializer(data=cart_item_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a cart item.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        """
        When updating a cart item, fetch new product info if product changes
        """
        instance = serializer.instance
        validated_data = serializer.validated_data

        # If product is changing, fetch new product info
        if ('product_type' in validated_data and validated_data['product_type'] != instance.product_type) or \
           ('product_id' in validated_data and validated_data['product_id'] != instance.product_id):

            product_type = validated_data.get('product_type', instance.product_type)
            product_id = validated_data.get('product_id', instance.product_id)

            # Get product base URL
            base_url = PRODUCT_SERVICE_URLS.get(product_type.lower())
            if not base_url:
                raise serializers.ValidationError(f"Unsupported product type: {product_type}")

            # Fetch product data
            url = f"{base_url}/{product_id}/"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    raise serializers.ValidationError(f"Product service error: {response.status_code}")
                product_data = response.json()
            except requests.RequestException as e:
                raise serializers.ValidationError(f"Product service unavailable: {str(e)}")

            # Update product details
            validated_data['product_name'] = product_data.get('title', product_data.get('name', 'Unknown'))
            validated_data['price'] = product_data.get('price', 0)

        serializer.save()

class CustomerCartView(generics.ListAPIView):
    """
    Get all carts for a specific customer
    """
    serializer_class = CartSerializer

    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')
        return Cart.objects.filter(customer_id=customer_id).order_by('-created')