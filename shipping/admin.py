from django_mongoengine import mongo_admin
from .models import ShippingMethod, ShippingRate

class ShippingMethodAdmin(mongo_admin.DocumentAdmin):
    list_display = ('name', 'carrier', 'estimated_days', 'tracking_available', 'is_active')
    list_filter = ('carrier', 'tracking_available', 'is_active')
    search_fields = ('name', 'carrier')
    ordering = ['carrier']

class ShippingRateAdmin(mongo_admin.DocumentAdmin):
    ordering = ['base_rate']
    list_filter = ['country', 'is_active']  # Only use these fields

    # Other configuration remains the same
    list_display = ('country', 'base_rate', 'weight_rate', 'min_weight', 'max_weight', 'is_active')
    search_fields = ('country',)

mongo_admin.site.register(ShippingMethod, ShippingMethodAdmin)
mongo_admin.site.register(ShippingRate, ShippingRateAdmin)