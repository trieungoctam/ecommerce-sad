import datetime
from rest_framework_mongoengine.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Clothes
from .serializers import ClothesSerializer

class ClothesViewSet(ModelViewSet):
    serializer_class = ClothesSerializer
    lookup_field = 'id'  # MongoEngine sử dụng id dạng ObjectId
    queryset = Clothes.objects.all()

    def perform_create(self, serializer):
        serializer.validated_data['created'] = serializer.validated_data.get('created', None) or datetime.datetime.now()
        serializer.validated_data['updated'] = datetime.datetime.now()
        serializer.save()

    def perform_update(self, serializer):
        serializer.validated_data['updated'] = datetime.datetime.now()
        serializer.save()

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Tìm kiếm quần áo theo tên hoặc thương hiệu.
        Ví dụ: /api/clothes/search/?q=Nike
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "Vui lòng cung cấp tham số tìm kiếm 'q'."}, status=status.HTTP_400_BAD_REQUEST)
        # Tìm kiếm theo tên hoặc thương hiệu (không phân biệt hoa thường)
        results = Clothes.objects.filter(name__icontains=query) | Clothes.objects.filter(brand__icontains=query)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
