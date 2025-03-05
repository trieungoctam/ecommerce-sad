from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Shoes
from .serializers import ShoesSerializer

# Create your views here.

@action(detail=True, methods=['get'])
def size_chart(self, request, pk=None):
    """Get detailed size chart for the shoe."""
    shoes = self.get_object(pk)
    if not shoes:
        return Response(
            {"error": "Shoes not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    return Response({
        'size_chart': shoes.size_chart,
        'fit_type': shoes.fit_type,
        'available_sizes': {
            'US': shoes.get_available_sizes_for_region('US'),
            'UK': shoes.get_available_sizes_for_region('UK'),
            'EU': shoes.get_available_sizes_for_region('EU'),
            'CM': shoes.get_available_sizes_for_region('CM')
        }
    })

@action(detail=True, methods=['post'])
def update_size_inventory(self, request, pk=None):
    """Update inventory for specific sizes."""
    shoes = self.get_object(pk)
    if not shoes:
        return Response(
            {"error": "Shoes not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    size_data = request.data.get('size_inventory')
    if not size_data or not isinstance(size_data, dict):
        return Response(
            {"error": "Invalid size inventory data"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        shoes.update_size_inventory(size_data)
        return Response(ShoesSerializer(shoes).data)
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@action(detail=True, methods=['get'])
def inventory_status(self, request, pk=None):
    """Get detailed inventory status including low stock alerts."""
    shoes = self.get_object(pk)
    if not shoes:
        return Response(
            {"error": "Shoes not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    low_stock_sizes = [
        size for size, qty in shoes.size_inventory.items()
        if int(qty) <= shoes.low_stock_threshold
    ]

    return Response({
        'total_stock': shoes.stock,
        'size_inventory': shoes.size_inventory,
        'low_stock_threshold': shoes.low_stock_threshold,
        'low_stock_sizes': low_stock_sizes,
        'is_low_stock': shoes.is_low_stock(),
        'is_discontinued': shoes.is_discontinued
    })

@action(detail=True, methods=['post'])
def toggle_discontinued(self, request, pk=None):
    """Toggle discontinued status of the shoe."""
    shoes = self.get_object(pk)
    if not shoes:
        return Response(
            {"error": "Shoes not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    shoes.is_discontinued = not shoes.is_discontinued
    shoes.save()
    return Response({
        'status': 'success',
        'is_discontinued': shoes.is_discontinued
    })

@action(detail=False, methods=['get'])
def sustainability(self, request):
    """Get shoes sorted by sustainability rating."""
    min_rating = request.query_params.get('min_rating', 1)
    try:
        min_rating = int(min_rating)
        if not 1 <= min_rating <= 5:
            raise ValueError
    except ValueError:
        return Response(
            {"error": "Invalid minimum rating"},
            status=status.HTTP_400_BAD_REQUEST
        )

    shoes = Shoes.objects.filter(
        sustainability_rating__gte=min_rating
    ).order_by('-sustainability_rating')

    serializer = ShoesSerializer(shoes, many=True)
    return Response(serializer.data)

@action(detail=False, methods=['get'])
def fit_guide(self, request):
    """Get shoes filtered by fit type."""
    fit_type = request.query_params.get('fit_type')
    if not fit_type:
        return Response(
            {"error": "Fit type parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    shoes = Shoes.objects.filter(fit_type=fit_type)
    serializer = ShoesSerializer(shoes, many=True)
    return Response(serializer.data)
