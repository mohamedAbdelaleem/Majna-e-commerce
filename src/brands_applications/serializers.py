from rest_framework import serializers
from .models import BrandApplication


class BrandApplicationInputSerializer(serializers.Serializer):
    authorization_doc = serializers.FileField()
    identity_doc = serializers.FileField()
    



