from django_mongoengine import mongo_admin
from .models import Shoes

class ShoesAdmin(mongo_admin.DocumentAdmin):
    list_display = ('name', 'brand', 'category', 'gender', 'price', 'stock', 'sku')
    list_filter = (
        'category', 'gender', 'brand', 'style', 'occasion',
        'is_waterproof', 'is_orthopedic', 'is_athletic', 'has_arch_support'
    )
    search_fields = ('name', 'brand', 'sku', 'description')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'brand', 'sku', 'description', 'price', 'stock')
        }),
        ('Shoe Specifications', {
            'fields': ('category', 'gender', 'available_sizes', 'colors')
        }),
        ('Material and Construction', {
            'fields': ('upper_material', 'sole_material', 'closure_type', 'insole_type')
        }),
        ('Features', {
            'fields': ('is_waterproof', 'is_orthopedic', 'is_athletic', 'has_arch_support')
        }),
        ('Style and Usage', {
            'fields': ('style', 'occasion', 'season')
        }),
        ('Additional Information', {
            'fields': ('warranty', 'care_instructions', 'release_date')
        })
    )

mongo_admin.site.register(Shoes, ShoesAdmin)