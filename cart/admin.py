from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product_type', 'product_id', 'product_name', 'quantity', 'price', 'added_at')

class CartAdmin(admin.ModelAdmin):
    list_display = ('created',)
    inlines = [CartItemInline]
    search_fields = ('customer__email',)

admin.site.register(Cart, CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product_name', 'quantity', 'price', 'added_at')
    list_filter = ('product_type',)
    search_fields = ('product_name', 'product_id')

admin.site.register(CartItem, CartItemAdmin)