from rest_framework import serializers
from .models import Shoes, SizeConversion

class SizeConversionSerializer(serializers.Serializer):
    us = serializers.DecimalField(max_digits=4, decimal_places=1)
    uk = serializers.DecimalField(max_digits=4, decimal_places=1)
    eu = serializers.IntegerField()
    cm = serializers.DecimalField(max_digits=4, decimal_places=1)

class ShoesSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    brand = serializers.CharField(max_length=100)
    sku = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField(min_value=0)

    # Shoe Specifications
    category = serializers.CharField(max_length=50)
    gender = serializers.CharField(max_length=20)
    available_sizes = SizeConversionSerializer(many=True)
    colors = serializers.ListField(child=serializers.CharField(max_length=50))

    # Material and Construction
    upper_material = serializers.CharField(max_length=100, required=False)
    sole_material = serializers.CharField(max_length=100, required=False)
    closure_type = serializers.CharField(max_length=50, required=False)
    insole_type = serializers.CharField(max_length=100, required=False)

    # Features
    is_waterproof = serializers.BooleanField(default=False)
    is_orthopedic = serializers.BooleanField(default=False)
    is_athletic = serializers.BooleanField(default=False)
    has_arch_support = serializers.BooleanField(default=False)

    # Style and Usage
    style = serializers.CharField(max_length=50, required=False)
    occasion = serializers.CharField(max_length=50, required=False)
    season = serializers.ListField(child=serializers.CharField(max_length=20), required=False)

    # Additional Information
    warranty = serializers.IntegerField(min_value=0, default=0)
    care_instructions = serializers.CharField(required=False, allow_blank=True)
    release_date = serializers.DateTimeField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Size Information
    size_chart = serializers.DictField(required=False)
    fit_type = serializers.CharField(max_length=50, required=False)
    heel_height = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)
    weight = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)

    # Inventory Management
    size_inventory = serializers.DictField(required=False)
    low_stock_threshold = serializers.IntegerField(default=5)
    is_discontinued = serializers.BooleanField(default=False)

    # Additional Features
    sustainability_rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    comfort_rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    durability_rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    return_policy = serializers.CharField(required=False, allow_blank=True)
    shipping_weight = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)
    box_dimensions = serializers.CharField(required=False)

    def create(self, validated_data):
        return Shoes.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_gender(self, value):
        valid_genders = ['Men', 'Women', 'Unisex', 'Kids']
        if value not in valid_genders:
            raise serializers.ValidationError(f"Gender must be one of {valid_genders}")
        return value

    def validate_category(self, value):
        valid_categories = [
            'Sneakers', 'Running', 'Basketball', 'Tennis',
            'Boots', 'Hiking', 'Work', 'Rain',
            'Formal', 'Dress', 'Oxford', 'Loafers',
            'Casual', 'Slip-ons', 'Sandals', 'Slippers'
        ]
        if value not in valid_categories:
            raise serializers.ValidationError(f"Category must be one of {valid_categories}")
        return value

    def validate_fit_type(self, value):
        valid_fit_types = ['Regular', 'Wide', 'Narrow']
        if value and value not in valid_fit_types:
            raise serializers.ValidationError(f"Fit type must be one of {valid_fit_types}")
        return value

    def validate_size_inventory(self, value):
        try:
            for size, quantity in value.items():
                if not isinstance(quantity, int) or quantity < 0:
                    raise serializers.ValidationError(f"Invalid quantity for size {size}")
        except (ValueError, AttributeError):
            raise serializers.ValidationError("Invalid size inventory format")
        return value

    def validate_available_sizes(self, value):
        if not value:
            raise serializers.ValidationError("At least one size must be specified")

        for size in value:
            if not all(key in size for key in ['us', 'uk', 'eu', 'cm']):
                raise serializers.ValidationError("Each size must include US, UK, EU, and CM measurements")

            # Validate reasonable size ranges
            if not (3 <= size['us'] <= 20):
                raise serializers.ValidationError("US size must be between 3 and 20")
            if not (2 <= size['uk'] <= 19):
                raise serializers.ValidationError("UK size must be between 2 and 19")
            if not (35 <= size['eu'] <= 50):
                raise serializers.ValidationError("EU size must be between 35 and 50")
            if not (20 <= size['cm'] <= 35):
                raise serializers.ValidationError("CM size must be between 20 and 35")

        return value

    def validate_season(self, value):
        valid_seasons = ['Spring', 'Summer', 'Fall', 'Winter', 'All Season']
        for season in value:
            if season not in valid_seasons:
                raise serializers.ValidationError(f"Season must be one of {valid_seasons}")
        return value