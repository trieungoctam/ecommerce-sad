from rest_framework_mongoengine.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer

class BookViewSet(ModelViewSet):
    serializer_class = BookSerializer
    lookup_field = 'id'  # MongoEngine sử dụng id dạng ObjectId
    queryset = Book.objects.all()

    def perform_create(self, serializer):
        # Cập nhật thời gian tạo và cập nhật
        serializer.validated_data['created'] = serializer.validated_data.get('created', None) or datetime.datetime.utcnow()
        serializer.validated_data['updated'] = datetime.datetime.utcnow()
        serializer.save()

    def perform_update(self, serializer):
        # Cập nhật lại trường updated khi cập nhật sách
        serializer.validated_data['updated'] = datetime.datetime.utcnow()
        serializer.save()

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Tìm kiếm sách theo tiêu đề hoặc tác giả.
        Ví dụ: /api/books/search/?q=Harry
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "Please provide a search query using parameter 'q'."}, status=status.HTTP_400_BAD_REQUEST)
        books = Book.objects.filter(title__icontains=query) | Book.objects.filter(author__icontains=query)
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_price(self, request, id=None):
        """
        Cập nhật giá sách.
        Endpoint: /api/books/{id}/update_price/
        Yêu cầu JSON: {"price": 29.99}
        """
        book = self.get_object()
        new_price = request.data.get('price')
        if new_price is None:
            return Response({"detail": "Price not provided."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            book.price = float(new_price)
            book.updated = datetime.datetime.utcnow()
            book.save()
            serializer = self.get_serializer(book)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
