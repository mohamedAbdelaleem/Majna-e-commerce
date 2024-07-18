from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from common.api.paginator import ProductPagination
from products import models
from products import serializers
from products import services


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = models.Category.objects.all()
        serializer = serializers.CategoryOutSerializer(categories, many=True)
        return Response(data={"categories": serializer.data}, status=status.HTTP_200_OK)


class CategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, **kwargs):
        category_pk = kwargs["pk"]
        category = get_object_or_404(models.Category, pk=category_pk)
        serializer = serializers.CategoryOutSerializer(category)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CategoryProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, **kwargs):
        category_pk = kwargs["pk"]
        category = get_object_or_404(models.Category, pk=category_pk)

        query_params = serializers.ProductListQueryParametersSerializer(
            data=request.query_params
        )
        query_params.is_valid(raise_exception=True)

        selector = services.ProductSelector()
        products = selector.category_product_list(
            category.pk, **query_params.validated_data
        )

        paginator = ProductPagination()
        products = products.prefetch_related("brand")
        paginated_dataset = paginator.paginate_queryset(products, request)

        serializer = serializers.ProductListOutSerializer(
            paginated_dataset, many=True, context={"request": request}
        )
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response


