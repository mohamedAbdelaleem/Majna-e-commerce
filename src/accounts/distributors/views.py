from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from common.api.permissions import DistributorsOnly
from common.api.paginator import ProductPagination
from brands.services import BrandSelector
from brands.serializers import BrandOutSerializer
from brands_applications.services import BrandApplicationSelector
from brands_applications.serializers import BrandApplicationListOutSerializer
from products.services import ProductSelector, ProductService
from products.serializers import (
    ProductListOutSerializer,
    ProductUpdateInputSerializer,
    ProductOutSerializer,
)
from products.models import Product


class DistributorBrandsView(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]

    def get(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Access to this resource is denied")

        selector = BrandSelector()
        brand_list = selector.brand_list(distributors__pk=distributor_pk)
        data = BrandOutSerializer(
            brand_list, many=True, context={"request": request}
        ).data

        return Response(data)


class DistributorBrandApplicationsView(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]

    def get(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Access to this resource is denied")

        selector = BrandApplicationSelector()
        brand_list = selector.brand_application_list(distributor__pk=distributor_pk)
        data = BrandApplicationListOutSerializer(
            brand_list, many=True, context={"request": request}
        ).data

        return Response(data)


class DistributorProductListView(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]

    def get(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Access to this resource is denied")

        selector = ProductSelector()
        products = selector.product_list(
            inventory__store__distributor_id=distributor_pk, ordering=["-id"]
        )
        paginator = ProductPagination()
        products = products.prefetch_related("brand")
        paginated_dataset = paginator.paginate_queryset(products, request)
        serializer = ProductListOutSerializer(
            paginated_dataset, many=True, context={"request": request}
        )
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response


class ProductDetailUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]

    def get(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Access to this resource is denied")

        product_pk = kwargs["product_pk"]
        product = get_object_or_404(Product, pk=product_pk)
        selector = ProductSelector()
        if not selector.is_owner(distributor_pk, product_pk):
            raise PermissionDenied("Access to this resource is denied")
        
        serializer = ProductOutSerializer(product, context={"request": request})

        return Response(serializer.data)

    def patch(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Access to this resource is denied")

        product_pk = kwargs["product_pk"]
        product = get_object_or_404(Product, pk=product_pk)
        selector = ProductSelector()
        if not selector.is_owner(distributor_pk, product_pk):
            raise PermissionDenied("Access to this resource is denied")
        
        serializer = ProductUpdateInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        service = ProductService()
        service.update(product, distributor_pk, **serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Access to this resource is denied")

        product_pk = kwargs["product_pk"]
        product = get_object_or_404(Product, pk=product_pk)
        selector = ProductSelector()
        if not selector.is_owner(distributor_pk, product_pk):
            raise PermissionDenied("Access to this resource is denied")

        service = ProductService()
        service.delete(product)

        return Response(status=status.HTTP_204_NO_CONTENT)
