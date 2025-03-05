from django_mongoengine import mongo_admin
from .models import Book

class BookAdmin(mongo_admin.DocumentAdmin):
    list_display = ('title', 'author', 'price', 'available')
    search_fields = ('title', 'author', 'isbn')

mongo_admin.site.register(Book, BookAdmin)