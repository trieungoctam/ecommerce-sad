from rest_framework import generics, permissions
from rest_framework import status, serializers
from rest_framework.response import Response
from .models import Customer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomerRegistrationSerializer, CustomerSerializer, CustomTokenObtainPairSerializer

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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response(
                {'detail': e.detail},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)