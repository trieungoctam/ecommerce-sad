import datetime
from rest_framework_mongoengine.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Shoe
from .serializers import ShoeSerializer

class ShoeViewSet(ModelViewSet):
    serializer_class = ShoeSerializer
    lookup_field = 'id'  # MongoEngine sử dụng id dạng ObjectId
    queryset = Shoe.objects.all()

    def perform_create(self, serializer):
        # Thiết lập thời gian tạo và cập nhật
        serializer.validated_data['created'] = serializer.validated_data.get('created', None) or datetime.datetime.now()
        serializer.validated_data['updated'] = datetime.datetime.now()
        serializer.save()

    def perform_update(self, serializer):
        serializer.validated_data['updated'] = datetime.datetime.now()
        serializer.save()

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Tìm kiếm giày theo tên hoặc thương hiệu.
        Ví dụ: /api/shoes/search/?q=Nike
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "Vui lòng cung cấp tham số tìm kiếm 'q'."}, status=status.HTTP_400_BAD_REQUEST)
        # Tìm kiếm theo tên sản phẩm hoặc thương hiệu (không phân biệt hoa thường)
        shoes = Shoe.objects.filter(name__icontains=query) | Shoe.objects.filter(brand__icontains=query)
        serializer = self.get_serializer(shoes, many=True)
        return Response(serializer.data)
