from rest_framework import serializers
from stores.models import City, Governorate


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "name_ar"]

class GovernorateSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)
    class Meta:
        model = Governorate
        fields = ["id", "name", "name_ar", "cities"]