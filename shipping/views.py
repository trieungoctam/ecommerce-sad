from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import ShippingMethod, ShippingRate
from .serializers import ShippingMethodSerializer, ShippingRateSerializer, AddressSerializer

# Create your views here.

class ShippingMethodViewSet(viewsets.ModelViewSet):
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        shipping_method = self.get_object()
        shipping_method.is_active = not shipping_method.is_active
        shipping_method.save()
        return Response({
            'status': f"Shipping method {'activated' if shipping_method.is_active else 'deactivated'}",
            'is_active': shipping_method.is_active
        })

class ShippingRateViewSet(viewsets.ModelViewSet):
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = ShippingRate.objects.all()
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(country=country)
        return queryset.filter(is_active=True)

    @action(detail=False, methods=['post'])
    def calculate_shipping(self, request):
        """Calculate shipping cost for given weight and destination."""
        country = request.data.get('country')
        weight = request.data.get('weight')

        if not country or not weight:
            return Response(
                {'error': 'Both country and weight are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            weight = float(weight)
        except ValueError:
            return Response(
                {'error': 'Invalid weight value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find all applicable shipping rates for the country
        shipping_rates = ShippingRate.objects.filter(
            country=country,
            is_active=True,
            min_weight__lte=weight,
            max_weight__gte=weight
        )

        if not shipping_rates:
            return Response(
                {'error': 'No shipping options available for the specified criteria'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate costs for all available shipping methods
        shipping_options = []
        for rate in shipping_rates:
            try:
                cost = rate.calculate_shipping_cost(weight)
                shipping_options.append({
                    'shipping_method': ShippingMethodSerializer(rate.shipping_method).data,
                    'cost': cost,
                    'estimated_days': rate.shipping_method.estimated_days
                })
            except ValueError as e:
                continue

        return Response({
            'country': country,
            'weight': weight,
            'shipping_options': shipping_options
        })

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        shipping_rate = self.get_object()
        shipping_rate.is_active = not shipping_rate.is_active
        shipping_rate.save()
        return Response({
            'status': f"Shipping rate {'activated' if shipping_rate.is_active else 'deactivated'}",
            'is_active': shipping_rate.is_active
        })

class AddressViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def validate_address(self, request):
        """Validate shipping address."""
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            # Here you could add additional address validation logic
            # For example, using external address validation services
            return Response({
                'status': 'valid',
                'normalized_address': serializer.validated_data
            })
        return Response(
            {'status': 'invalid', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
