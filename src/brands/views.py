from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from common.api.permissions import DistributorsOnly
from brands_applications.serializers import BrandApplicationInputSerializer
from brands_applications.services import BrandApplicationService
from .models import Brand
from . import services
from .serializers import BrandOutSerializer


class BrandsView(APIView):

    def get(self, request):
        brand_selector = services.BrandSelector()
        brands = brand_selector.brand_list()
        data = BrandOutSerializer(brands, many=True, context={'request':request}).data
        data = {"brands": data}
        return Response(data=data, status=status.HTTP_200_OK)
    

class BrandView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs['pk']
        brand = get_object_or_404(Brand, pk=pk)
        data = BrandOutSerializer(brand, context={'request':request}).data
        return Response(data=data, status=status.HTTP_200_OK)


class BrandApplicationsView(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, **kwargs):
        brand = get_object_or_404(Brand, pk=kwargs["pk"])
        distributor_id = request.user.id

        serializer = BrandApplicationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BrandApplicationService()
        
        service.create(
            brand=brand,
            distributor_id=distributor_id,
            authorization_doc=serializer.validated_data["authorization_doc"],
            identity_doc=serializer.validated_data["identity_doc"],
        )

        return Response(data={"message": "Created"}, status=status.HTTP_201_CREATED)
