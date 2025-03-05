from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import ValidationError
from mongoengine.errors import DoesNotExist, NotUniqueError
from .models import Clothes
from .serializers import ClothesSerializer

# Create your views here.

class ClothesViewSet(viewsets.ViewSet):
    """
    ViewSet for managing clothes.
    Provides CRUD operations and filtering capabilities.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Clothes.objects.get(id=pk)
        except DoesNotExist:
            return None

    def list(self, request):
        """
        List clothes with optional filtering.
        Query params: category, gender, brand, price_min, price_max, size, color
        """
        queryset = Clothes.objects.all()

        # Apply filters
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        gender = request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)

        brand = request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        price_min = request.query_params.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))

        price_max = request.query_params.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=float(price_max))

        size = request.query_params.get('size')
        if size:
            queryset = queryset.filter(sizes=size)

        color = request.query_params.get('color')
        if color:
            queryset = queryset.filter(colors=color)

        serializer = ClothesSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ClothesSerializer(data=request.data)
        if serializer.is_valid():
            try:
                clothes = serializer.save()
                return Response(
                    ClothesSerializer(clothes).data,
                    status=status.HTTP_201_CREATED
                )
            except NotUniqueError:
                return Response(
                    {"error": "SKU already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        clothes = self.get_object(pk)
        if not clothes:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ClothesSerializer(clothes)
        return Response(serializer.data)

    def update(self, request, pk=None):
        clothes = self.get_object(pk)
        if not clothes:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClothesSerializer(clothes, data=request.data)
        if serializer.is_valid():
            try:
                clothes = serializer.save()
                return Response(ClothesSerializer(clothes).data)
            except NotUniqueError:
                return Response(
                    {"error": "SKU already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        clothes = self.get_object(pk)
        if not clothes:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        clothes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get list of all available categories."""
        categories = Clothes.objects.distinct('category')
        return Response(categories)

    @action(detail=False, methods=['get'])
    def brands(self, request):
        """Get list of all available brands."""
        brands = Clothes.objects.distinct('brand')
        return Response(brands)

    @action(detail=False, methods=['get'])
    def sizes(self, request):
        """Get list of all available sizes."""
        sizes = Clothes.objects.distinct('sizes')
        return Response(sizes)

    @action(detail=False, methods=['get'])
    def colors(self, request):
        """Get list of all available colors."""
        colors = Clothes.objects.distinct('colors')
        return Response(colors)

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update stock quantity."""
        clothes = self.get_object(pk)
        if not clothes:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        stock = request.data.get('stock')
        if stock is None:
            return Response(
                {"error": "Stock quantity is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "Invalid stock quantity"},
                status=status.HTTP_400_BAD_REQUEST
            )

        clothes.stock = stock
        clothes.save()
        return Response(ClothesSerializer(clothes).data)
