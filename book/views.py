from rest_framework_mongoengine.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer

from rest_framework import generics, permissions
import datetime

class BookListView(generics.ListCreateAPIView):
    """
    Tạo sách mới hoặc lấy danh sách tất cả sách.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Cập nhật thời gian tạo và cập nhật
        current_time = datetime.datetime.now()
        serializer.validated_data['created'] = current_time
        serializer.validated_data['updated'] = current_time
        serializer.save()

    def list(self, request, *args, **kwargs):
        # Lấy danh sách tất cả sách, mặc định sắp xếp theo thời gian tạo mới nhất
        queryset = self.filter_queryset(self.get_queryset())

        # Phân trang nếu cần
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Xem chi tiết, cập nhật hoặc xóa một quyển sách.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'  # MongoEngine sử dụng id dạng ObjectId

    def perform_update(self, serializer):
        # Cập nhật lại trường updated khi cập nhật sách
        serializer.validated_data['updated'] = datetime.datetime.now()
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
class BookCreateView(generics.CreateAPIView):
    """
    Tạo sách mới.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [BearerTokenAuthentication]

    def perform_create(self, serializer):
        # Cập nhật thời gian tạo và cập nhật
        current_time = datetime.datetime.now()
        serializer.validated_data['created'] = current_time
        serializer.validated_data['updated'] = current_time
        serializer.save()

    # @action(detail=True, methods=['post'])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    'success': True,
                    'message': 'Sách đã được tạo thành công',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(
            {
                'success': False,
                'message': 'Dữ liệu không hợp lệ',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

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
