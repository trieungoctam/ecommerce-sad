from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Clothes

class ClothesSerializer(DocumentSerializer):
    class Meta:
        model = Clothes
        fields = '__all__'
