from rest_framework import serializers
from .models import BrandApplication


class BrandApplicationInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrandApplication
        fields = ['authorization_doc', 'identity_doc']



