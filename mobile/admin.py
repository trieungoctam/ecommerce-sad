from django_mongoengine import mongo_admin
from .models import Mobile

class MobileAdmin(mongo_admin.DocumentAdmin):
    list_display = ('name', 'brand', 'model_number', 'price', 'ram', 'storage', 'network', 'stock')
    list_filter = ('brand', 'network', 'ram', 'storage', 'operating_system',
                  'dual_sim', 'wireless_charging', 'water_resistant')
    search_fields = ('name', 'brand', 'model_number', 'description', 'processor')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'brand', 'model_number', 'description', 'price', 'stock')
        }),
        ('Technical Specifications', {
            'fields': ('screen_size', 'ram', 'storage', 'battery_capacity',
                      'processor', 'operating_system', 'camera_specs')
        }),
        ('Features', {
            'fields': ('colors', 'network', 'dual_sim', 'fingerprint_sensor',
                      'face_unlock', 'wireless_charging', 'fast_charging', 'water_resistant')
        }),
        ('Additional Information', {
            'fields': ('warranty', 'release_date')
        })
    )


mongo_admin.site.register(Mobile, MobileAdmin)