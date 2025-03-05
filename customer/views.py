from rest_framework import generics, permissions
from .models import Customer
from .serializers import CustomerRegistrationSerializer, CustomerSerializer

class CustomerRegistrationView(generics.CreateAPIView):
    """
    Endpoint đăng ký khách hàng mới.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CustomerDetailView(generics.RetrieveUpdateAPIView):
    """
    Lấy chi tiết và cập nhật thông tin khách hàng.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'id'