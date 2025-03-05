from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Shoe

class ShoeSerializer(DocumentSerializer):
    class Meta:
        model = Shoe
        fields = '__all__'
