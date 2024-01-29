from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from common.api.permissions import DistributorsOnly
from brands_applications.serializers import BrandApplicationInputSerializer
from brands_applications.services import BrandApplicationService
from .models import Brand
from . import services


class BrandsView(APIView):
    class OutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Brand
            fields = ["id", "name"]

    def get(self, request):
        brand_selector = services.BrandSelector()
        brands = brand_selector.brand_list()
        data = self.OutSerializer(brands, many=True).data
        data = {"brands": data}
        return Response(data=data, status=status.HTTP_200_OK)


class BrandApplications(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, **kwargs):
        brand = get_object_or_404(Brand, pk=kwargs["pk"])
        distributor_id = request.user.id

        serializer = BrandApplicationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BrandApplicationService()
        
        authorization_doc=serializer.validated_data["authorization_doc"]
        identity_doc=serializer.validated_data["identity_doc"]
        service.create(
            brand=brand,
            distributor_id=distributor_id,
            authorization_doc=serializer.validated_data["authorization_doc"],
            identity_doc=serializer.validated_data["identity_doc"],
        )

        return Response(data={"message": "Created"}, status=status.HTTP_201_CREATED)
