from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from common.api.permissions import CustomersOnly
from .serializers import (
    CartItemInputSerializer,
    CartItemOutSerializer,
    CartItemUpdateInputSerializer,
)
from .services import CartItemService, CartItemSelector
from .models import CartItem


class CartItemListCreate(APIView):
    permission_classes = [IsAuthenticated, CustomersOnly]

    def post(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied(
                "Customers can add cart items to just their own carts!"
            )

        serializer = CartItemInputSerializer(data=request.data)
        serializer.is_valid()
        service = CartItemService()
        service.bulk_create(**serializer.validated_data, customer_id=customer_pk)

        return Response(
            data={"message": "Cart item added successfully"},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Items of another user")

        selector = CartItemSelector()
        cart_items = selector.cart_item_list(customer_id=customer_pk)
        cart_items.prefetch_related("product")
        serializer = CartItemOutSerializer(
            instance=cart_items, many=True, context={"request": request}
        )
        data = {"cart_items": serializer.data}

        return Response(data=data, status=status.HTTP_200_OK)


class CartItemDetail(APIView):
    permission_classes = [IsAuthenticated, CustomersOnly]

    def get(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Item of another user")

        cart_item_pk = kwargs["cart_item_pk"]
        cart_item = get_object_or_404(
            CartItem, pk=cart_item_pk, customer_id=customer_pk
        )
        serializer = CartItemOutSerializer(
            instance=cart_item, context={"request": request}
        )
        data = {"cart_item": serializer.data}

        return Response(data=data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Item of another user")

        cart_item_pk = kwargs["cart_item_pk"]
        cart_item = get_object_or_404(
            CartItem, pk=cart_item_pk, customer_id=customer_pk
        )
        serializer = CartItemUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = CartItemService()
        service.update_quantity(cart_item, serializer.validated_data["quantity"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Item of another user")

        cart_item_pk = kwargs["cart_item_pk"]
        cart_item = get_object_or_404(
            CartItem, pk=cart_item_pk, customer_id=customer_pk
        )

        service = CartItemService()
        service.cart_item_delete(cart_item)

        return Response(status=status.HTTP_204_NO_CONTENT)
