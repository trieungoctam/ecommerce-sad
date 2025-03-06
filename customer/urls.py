from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CustomerRegistrationView, CustomerDetailView, CustomTokenObtainPairView

urlpatterns = [
    # Endpoint đăng ký (không cần auth)
    path('register/', CustomerRegistrationView.as_view(), name='customer-register'),

    # Endpoint lấy token (đăng nhập)
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Endpoint refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoint lấy/chỉnh sửa thông tin cá nhân (yêu cầu authentication)
    path('<int:id>/', CustomerDetailView.as_view(), name='customer-detail'),
]