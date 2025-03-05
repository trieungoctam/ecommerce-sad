from rest_framework import serializers
from .models import Clothes

class ClothesSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    brand = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    sizes = serializers.ListField(child=serializers.CharField(max_length=10))
    colors = serializers.ListField(child=serializers.CharField(max_length=50))
    material = serializers.CharField(max_length=100, required=False)
    gender = serializers.CharField(max_length=20)
    stock = serializers.IntegerField(min_value=0)
    sku = serializers.CharField(max_length=50)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Clothes.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_gender(self, value):
        valid_genders = ['Men', 'Women', 'Unisex']
        if value not in valid_genders:
            raise serializers.ValidationError(f"Gender must be one of {valid_genders}")
        return value

    def validate_category(self, value):
        valid_categories = [
            'Shirt', 'T-Shirt', 'Pants', 'Jeans', 'Dress',
            'Skirt', 'Jacket', 'Coat', 'Sweater', 'Hoodie',
            'Underwear', 'Socks', 'Swimwear', 'Activewear'
        ]
        if value not in valid_categories:
            raise serializers.ValidationError(f"Category must be one of {valid_categories}")
        return value