from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import FormParser
from rest_framework.exceptions import PermissionDenied
from common.api.permissions import DistributorsOnly, CustomersOnly
from common.api.paginator import ProductPagination
from common.api.parsers import MultipartJsonParser
from . import models
from . import serializers
from . import services


class ProductListCreateView(APIView):
    parser_classes = [MultipartJsonParser, FormParser]

    def get_permissions(self):
        if self.request.method == "POST":
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
            paginated_dataset, many=True, context={"request": request}
        )
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, **kwargs):
        pk = kwargs["pk"]
        product = get_object_or_404(models.Product, pk=pk)
        serializer = serializers.ProductOutSerializer(
            product, context={"request": request}
        )

        return Response(serializer.data)


class FavoriteItemListCreate(APIView):
    permission_classes = [IsAuthenticated, CustomersOnly]

    def post(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied(
                "Customers can add cart items to just their own carts!"
            )

        serializer = serializers.FavoriteItemInputSerializer(data=request.data)
        serializer.is_valid()
        service = services.ProductService()
        service.bulk_add_to_favorite(
            serializer.validated_data["product_ids"], customer_pk
        )

        return Response(
            data={"message": "Favorite items added successfully"},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Items of another user")

        selector = services.ProductSelector()
        cart_items = selector.favorite_item_list(customer_id=customer_pk)
        cart_items.prefetch_related("product")
        serializer = serializers.FavoriteItemOutSerializer(
            instance=cart_items, many=True, context={"request": request}
        )
        data = {"favorite_items": serializer.data}

        return Response(data=data, status=status.HTTP_200_OK)


class FavoriteItemDelete(APIView):
    permission_classes = [IsAuthenticated, CustomersOnly]

    def delete(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Item of another user")

        favorite_item_pk = kwargs["favorite_item_pk"]
        favorite_item = get_object_or_404(
            models.FavoriteItem, pk=favorite_item_pk, customer_id=customer_pk
        )

        service = services.ProductService()
        service.remove_from_favorite(favorite_item)

        return Response(status=status.HTTP_204_NO_CONTENT)
