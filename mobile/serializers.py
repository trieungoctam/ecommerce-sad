from rest_framework import serializers
from .models import Mobile

class MobileSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    brand = serializers.CharField(max_length=100)
    model_number = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField(min_value=0)

    # Technical Specifications
    screen_size = serializers.DecimalField(max_digits=3, decimal_places=1)
    ram = serializers.IntegerField(min_value=1)
    storage = serializers.IntegerField(min_value=1)
    battery_capacity = serializers.IntegerField(min_value=1000)
    processor = serializers.CharField(max_length=100)
    operating_system = serializers.CharField(max_length=50)
    camera_specs = serializers.CharField(max_length=200)

    # Features
    colors = serializers.ListField(child=serializers.CharField(max_length=50))
    network = serializers.CharField(max_length=20)
    dual_sim = serializers.BooleanField(default=False)
    fingerprint_sensor = serializers.BooleanField(default=True)
    face_unlock = serializers.BooleanField(default=True)
    wireless_charging = serializers.BooleanField(default=False)
    fast_charging = serializers.BooleanField(default=True)
    water_resistant = serializers.BooleanField(default=False)

    # Additional Information
    warranty = serializers.IntegerField(min_value=0, default=12)
    release_date = serializers.DateTimeField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Mobile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_network(self, value):
        valid_networks = ['4G', '5G']
        if value not in valid_networks:
            raise serializers.ValidationError(f"Network must be one of {valid_networks}")
        return value

    def validate_ram(self, value):
        if value > 32:  # Current practical limit for mobile RAM
            raise serializers.ValidationError("RAM value seems unrealistic")
        return value

    def validate_storage(self, value):
        if value > 1024:  # 1TB current practical limit
            raise serializers.ValidationError("Storage value seems unrealistic")
        return value

    def validate_battery_capacity(self, value):
        if value > 7000:  # Current practical limit for mobile batteries
            raise serializers.ValidationError("Battery capacity seems unrealistic")
        return value