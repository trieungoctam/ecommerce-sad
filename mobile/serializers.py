from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Mobile

class MobileSerializer(DocumentSerializer):
    class Meta:
        model = Mobile
        fields = '__all__'
