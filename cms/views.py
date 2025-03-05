from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from .models import Category, Banner, Promotion, Page, FAQ, Menu
from .serializers import (
    CategorySerializer, BannerSerializer, PromotionSerializer,
    PageSerializer, FAQSerializer, MenuSerializer
)

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(parent=None)  # Root categories only
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def all_categories(self, request):
        """Get all categories including children."""
        categories = Category.objects.filter(is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active banners."""
        now = timezone.now()
        position = request.query_params.get('position')

        banners = Banner.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )

        if position:
            banners = banners.filter(position=position)

        serializer = self.get_serializer(banners, many=True)
        return Response(serializer.data)

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active promotions."""
        now = timezone.now()
        promotions = Promotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        serializer = self.get_serializer(promotions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def validate_code(self, request, pk=None):
        """Validate a promotion code."""
        promotion = self.get_object()
        amount = request.data.get('amount', 0)

        if not promotion.is_valid:
            return Response(
                {'valid': False, 'message': 'Promotion is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if promotion.min_purchase > float(amount):
            return Response(
                {
                    'valid': False,
                    'message': f'Minimum purchase amount is {promotion.min_purchase}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'valid': True,
            'discount_type': promotion.discount_type,
            'discount_value': promotion.discount_value
        })

class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active pages."""
        pages = Page.objects.filter(is_active=True)
        serializer = self.get_serializer(pages, many=True)
        return Response(serializer.data)

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get FAQs grouped by category."""
        faqs = FAQ.objects.filter(is_active=True)
        categories = {}

        for faq in faqs:
            if faq.category not in categories:
                categories[faq.category] = []
            categories[faq.category].append(FAQSerializer(faq).data)

        return Response(categories)

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(parent=None)  # Root menu items only
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active menu structure."""
        menus = Menu.objects.filter(is_active=True, parent=None)
        serializer = self.get_serializer(menus, many=True)
        return Response(serializer.data)
