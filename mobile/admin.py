from django_mongoengine import mongo_admin
from .models import Mobile

class MobileAdmin(mongo_admin.DocumentAdmin):
    list_display = ('brand', 'model_name', 'operating_system', 'storage_capacity', 'ram', 'price', 'available', 'created')
    search_fields = ('brand', 'model_name', 'operating_system')

mongo_admin.site.register(Mobile, MobileAdmin)