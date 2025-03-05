from django_mongoengine import mongo_admin
from .models import Book

class BookAdmin(mongo_admin.DocumentAdmin):
    list_display = ('title', 'author', 'price', 'stock')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('published_date',)

mongo_admin.site.register(Book, BookAdmin)