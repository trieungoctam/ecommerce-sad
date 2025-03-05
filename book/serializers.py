from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Book

class BookSerializer(DocumentSerializer):
    class Meta:
        model = Book
        fields = '__all__'