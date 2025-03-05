from rest_framework import serializers
from .models import Category, Banner, Promotion, Page, FAQ, Menu

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'description',
            'image', 'is_active', 'order', 'children'
        ]

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []

class BannerSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(read_only=True)

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'image_url', 'link_url', 'position',
            'start_date', 'end_date', 'is_active', 'order',
            'is_current', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        return data

class PromotionSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'description', 'discount_type',
            'discount_value', 'code', 'start_date', 'end_date',
            'min_purchase', 'usage_limit', 'used_count',
            'is_active', 'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['used_count', 'created_at', 'updated_at']

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        if data['discount_type'] in ['PERCENTAGE', 'FIXED']:
            if data['discount_value'] <= 0:
                raise serializers.ValidationError(
                    "Discount value must be greater than 0"
                )
            if data['discount_type'] == 'PERCENTAGE' and data['discount_value'] > 100:
                raise serializers.ValidationError(
                    "Percentage discount cannot exceed 100%"
                )
        return data

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'content', 'meta_description',
            'meta_keywords', 'is_active', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'category',
            'is_active', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            'id', 'name', 'parent', 'link_url', 'order',
            'is_active', 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_children(self, obj):
        if obj.children.exists():
            return MenuSerializer(obj.children.all(), many=True).data
        return []