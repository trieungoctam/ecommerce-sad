from django.contrib import admin
from .models import Category, Banner, Promotion, Page, FAQ, Menu

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'start_date', 'end_date', 'is_active', 'order')
    list_filter = ('position', 'is_active', 'start_date', 'end_date')
    search_fields = ('title',)
    ordering = ('position', 'order', '-start_date')
    date_hierarchy = 'start_date'

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'discount_type', 'discount_value',
                   'start_date', 'end_date', 'is_active', 'used_count')
    list_filter = ('discount_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('title', 'code', 'description')
    readonly_fields = ('used_count',)
    date_hierarchy = 'start_date'

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'order')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer', 'category')
    ordering = ('category', 'order')

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'link_url', 'order', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'link_url')
    ordering = ('order', 'name')
