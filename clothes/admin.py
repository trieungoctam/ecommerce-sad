from django_mongoengine import mongo_admin
from .models import Clothes

class ClothesAdmin(mongo_admin.DocumentAdmin):
    list_display = ('name', 'brand', 'category', 'gender', 'price', 'stock', 'sku')
    list_filter = ('category', 'gender', 'brand', 'sizes', 'colors')
    search_fields = ('name', 'brand', 'sku', 'description')
    ordering = ('-created_at',)

mongo_admin.site.register(Clothes, ClothesAdmin)