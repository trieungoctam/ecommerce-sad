from django.contrib import admin
from .models import SearchHistory, PopularSearch

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'results_count', 'created_at')
    list_filter = ('created_at', 'results_count')
    search_fields = ('user__username', 'query')
    readonly_fields = ('user', 'query', 'filters', 'results_count', 'created_at')
    date_hierarchy = 'created_at'

@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'count', 'last_searched', 'created_at')
    list_filter = ('created_at', 'last_searched')
    search_fields = ('query',)
    readonly_fields = ('count', 'last_searched', 'created_at')
    ordering = ('-count',)
