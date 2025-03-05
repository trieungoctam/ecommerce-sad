from django_mongoengine import mongo_admin
from .models import Clothes

class ClothesAdmin(mongo_admin.DocumentAdmin):
    list_display = ('brand', 'name', 'size', 'price', 'available', 'created')
    search_fields = ('brand', 'name', 'color')

mongo_admin.site.register(Clothes, ClothesAdmin)