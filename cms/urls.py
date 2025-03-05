from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BannerViewSet, PromotionViewSet,
    PageViewSet, FAQViewSet, MenuViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'banners', BannerViewSet)
router.register(r'promotions', PromotionViewSet)
router.register(r'pages', PageViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'menus', MenuViewSet)

urlpatterns = [
    path('', include(router.urls)),
]