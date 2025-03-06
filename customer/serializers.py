from rest_framework import serializers
from .models import Customer, Address
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']

class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = Customer
        fields = ['id', 'email', 'full_name', 'user_type', 'address']
        read_only_fields = ['id', 'user_type']

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        # Cập nhật các trường của Customer
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Nếu có dữ liệu address, cập nhật hoặc tạo mới
        if address_data:
            # Nếu đã có address liên kết, cập nhật
            if hasattr(instance, 'address'):
                addr = instance.address
                for attr, value in address_data.items():
                    setattr(addr, attr, value)
                addr.save()
            else:
                Address.objects.create(customer=instance, **address_data)
        return instance

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    address = AddressSerializer(required=False)

    class Meta:
        model = Customer
        fields = ['email', 'full_name', 'user_type', 'password1', 'password2', 'address']
        extra_kwargs = {'user_type': {'default': Customer.UserType.REGISTERED}}

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match!")
        return data

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        password = validated_data.pop('password1')
        # Loại bỏ password2 vì đã kiểm tra
        validated_data.pop('password2')
        # Tạo user bằng manager (đảm bảo rằng user_type của admin chỉ được tạo qua create_superuser)
        customer = Customer.objects.create_user(password=password, **validated_data)
        if address_data:
            Address.objects.create(customer=customer, **address_data)
        return customer

Customer = get_user_model()

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Attempt to authenticate the user
            user = Customer.objects.get(email=email)

            # If authentication failed...
            if not user:
                msg = 'Không thể đăng nhập với thông tin đã cung cấp.'
                raise serializers.ValidationError(msg, code='authorization')

            # If user is not active...
            if not user.is_active:
                msg = 'Tài khoản này đã bị vô hiệu hóa.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Phải cung cấp cả "email" và "password".'
            raise serializers.ValidationError(msg, code='authorization')

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        # Add custom claims to token
        refresh['user_type'] = user.user_type
        refresh['email'] = user.email
        refresh['full_name'] = user.full_name

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'user_type': user.user_type
            }
        }