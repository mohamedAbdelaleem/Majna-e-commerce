from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import FormParser
from common.api.permissions import DistributorsOnly
from common.api.paginator import ProductPagination
from common.api.parsers import MultipartJsonParser
from . import models
from . import serializers
from . import services


class ProductListCreateView(APIView):
    parser_classes = [MultipartJsonParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), DistributorsOnly()]
        return [AllowAny()]

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

    def get(self, request, **kwargs):
        query_params = serializers.ProductListQueryParametersSerializer(
            data=request.query_params
        )
        query_params.is_valid(raise_exception=True)

        selector = services.ProductSelector() 
        products = selector.product_list(**query_params.validated_data)

        paginator = ProductPagination()
        products = products.prefetch_related("brand")
        paginated_dataset = paginator.paginate_queryset(products, request)

        serializer = serializers.ProductListOutSerializer(
            paginated_dataset, many=True, context = {'request': request}
        )
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response


class CategoryProductListView(APIView):

    def get(self, request, **kwargs):
        category_pk = kwargs['pk']
        category = get_object_or_404(models.Category, pk=category_pk)

        query_params = serializers.ProductListQueryParametersSerializer(
            data=request.query_params
        )
        query_params.is_valid(raise_exception=True)
        
        selector = services.ProductSelector() 
        products = selector.category_product_list(category.pk, **query_params.validated_data)

        paginator = ProductPagination()
        products = products.prefetch_related("brand")
        paginated_dataset = paginator.paginate_queryset(products, request)

        serializer = serializers.ProductListOutSerializer(
            paginated_dataset, many=True, context = {'request': request}
        )
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response


class CategoryListView(APIView):
    def get(self, request):
        categories = models.Category.objects.all()
        serializer = serializers.CategoryOutSerializer(categories, many=True)
        return Response(data={"categories": serializer.data}, status=status.HTTP_200_OK)


class SubCategoryListView(APIView):
    def get(self, request):
        categories = models.SubCategory.objects.all()
        serializer = serializers.SubCategoryOutSerializer(categories, many=True)
        return Response(
            data={"sub_categories": serializer.data}, status=status.HTTP_200_OK
        )
