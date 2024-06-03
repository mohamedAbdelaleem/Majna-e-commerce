from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser
from common.api.permissions import DistributorsOnly
from common.api.parsers import MultipartJsonParser
from . import models
from . import serializers
from . import services


class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]
    parser_classes = [MultipartJsonParser, FormParser]

    def post(self, request, *args, **kwargs):
        distributor_pk = request.user.pk
        serializer = serializers.ProductInputSerializer(data=request.data)

        if not serializer.is_valid():
            print(serializer.validated_data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(type(serializer.validated_data))
        service = services.ProductService()
        service.create(serializer.validated_data, distributor_pk)

        return Response(
            data={"message": "Product Created Successfully!"},
            status=status.HTTP_201_CREATED,
        )


class CategoryListView(APIView):
    def get(self, request):
        categories = models.Category.objects.all()
        serializer = serializers.CategoryOutSerializer(categories, many=True)
        return Response(data={"categories": serializer.data}, status=status.HTTP_200_OK)


class SubCategoryListView(APIView):
    def get(self, request):
        categories = models.SubCategory.objects.all()
        serializer = serializers.SubCategoryOutSerializer(categories, many=True)
        return Response(data={"sub_categories": serializer.data}, status=status.HTTP_200_OK)
