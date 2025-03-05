from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShoeViewSet

router = DefaultRouter()
router.register(r'', ShoeViewSet, basename='shoe')

urlpatterns = [
    path('', include(router.urls)),
]
