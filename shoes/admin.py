from django_mongoengine import mongo_admin
from .models import Shoe

class ShoeAdmin(mongo_admin.DocumentAdmin):
    list_display = ('brand', 'name', 'size', 'color', 'price', 'available', 'created')
    search_fields = ('brand', 'name', 'color')

mongo_admin.site.register(Shoe, ShoeAdmin)