from django.urls import reverse
from rest_framework import serializers
from .models import Store, PickupAddress, Governorate


class StoreInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["name", "city", "address"]


class StoreOutSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()
    governorate = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "governorate",
            "city",
            "city_id",
            "address",
            "creation_date",
            "distributor_id",
        ]

    def get_governorate(self, obj):
        governorate = obj.city.governorate
        return governorate.name

    def to_representation(self, instance):
        data = super().to_representation(instance)
        self_url = reverse(
            "distributors:store",
            kwargs={"pk": data["distributor_id"], "store_pk": data["id"]},
        )
        links = {
            "self": self.context["request"].build_absolute_uri(self_url),
        }

        data["_links"] = links
        return data


class PickupAddressInputSerializer(serializers.ModelSerializer):
    city_id = serializers.IntegerField()

    class Meta:
        model = PickupAddress
        fields = ["city_id", "address"]


class PickupAddressOutSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()

    class Meta:
        model = PickupAddress
        fields = ["id", "customer_id", "city", "city_id", "address"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        governorate = Governorate.objects.get(pk=instance.city.governorate_id)
        self_url = reverse(
            "customers:address",
            kwargs={"pk": instance.customer_id, "address_pk": instance.pk},
        )
        links = {"self": self.context["request"].build_absolute_uri(self_url)}
        data["governorate"] = governorate.name
        data["governorate_id"] = governorate.pk
        data["_links"] = links
        return data
