from rest_framework import serializers
from .models import SearchHistory, PopularSearch
from book.serializers import BookSerializer
from mobile.serializers import MobileSerializer
from shoes.serializers import ShoesSerializer

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'filters', 'results_count', 'created_at']
        read_only_fields = ['created_at']

class PopularSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularSearch
        fields = ['id', 'query', 'count', 'last_searched']
        read_only_fields = ['count', 'last_searched']

class UnifiedSearchResultSerializer(serializers.Serializer):
    type = serializers.CharField()  # 'book', 'mobile', 'shoes'
    id = serializers.CharField()
    name = serializers.CharField()
    brand = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    stock = serializers.IntegerField()
    image_url = serializers.URLField(required=False)
    rating = serializers.FloatField(required=False)
    details = serializers.DictField()  # Type-specific details

    def to_representation(self, instance):
        if instance._meta.model_name == 'book':
            return self._format_book(instance)
        elif instance._meta.model_name == 'mobile':
            return self._format_mobile(instance)
        elif instance._meta.model_name == 'shoes':
            return self._format_shoes(instance)
        return super().to_representation(instance)

    def _format_book(self, book):
        return {
            'type': 'book',
            'id': str(book.id),
            'name': book.title,
            'price': book.price,
            'description': book.description,
            'stock': book.stock,
            'details': {
                'author': book.author,
                'isbn': book.isbn,
                'published_date': book.published_date
            }
        }

    def _format_mobile(self, mobile):
        return {
            'type': 'mobile',
            'id': str(mobile.id),
            'name': mobile.name,
            'brand': mobile.brand,
            'price': mobile.price,
            'description': mobile.description,
            'stock': mobile.stock,
            'details': {
                'model_number': mobile.model_number,
                'screen_size': mobile.screen_size,
                'ram': mobile.ram,
                'storage': mobile.storage,
                'processor': mobile.processor,
                'operating_system': mobile.operating_system
            }
        }

    def _format_shoes(self, shoes):
        return {
            'type': 'shoes',
            'id': str(shoes.id),
            'name': shoes.name,
            'brand': shoes.brand,
            'price': shoes.price,
            'description': shoes.description,
            'category': shoes.category,
            'stock': shoes.stock,
            'details': {
                'gender': shoes.gender,
                'available_sizes': [
                    {'us': size.us, 'uk': size.uk, 'eu': size.eu}
                    for size in shoes.available_sizes
                ],
                'colors': shoes.colors,
                'style': shoes.style
            }
        }