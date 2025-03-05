import datetime
from rest_framework_mongoengine.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Mobile
from .serializers import MobileSerializer

class MobileViewSet(ModelViewSet):
    serializer_class = MobileSerializer
    lookup_field = 'id'  # MongoEngine sử dụng id dạng ObjectId
    queryset = Mobile.objects.all()

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
        Tìm kiếm điện thoại theo brand hoặc model_name.
        Ví dụ: /api/mobile/search/?q=iPhone
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "Please provide a search query using parameter 'q'."}, status=status.HTTP_400_BAD_REQUEST)
        # Tìm kiếm theo brand hoặc model_name (không phân biệt hoa thường)
        mobiles = Mobile.objects.filter(brand__icontains=query) | Mobile.objects.filter(model_name__icontains=query)
        serializer = self.get_serializer(mobiles, many=True)
        return Response(serializer.data)
