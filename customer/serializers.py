from rest_framework import serializers
from .models import Customer, Address

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
