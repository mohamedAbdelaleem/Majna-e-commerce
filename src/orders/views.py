from functools import partial
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from common.api.paginator import OrderPagination
from common.api.permissions import CustomersOnly, DeliveriesOnly
from orders.models import Order
from . import serializers
from . import services


class OrderListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), CustomersOnly()]
        return [IsAuthenticated(), DeliveriesOnly()]

    def post(self, request, **kwargs):
        customer_pk = request.user.pk
        serializer = serializers.OrderInputSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        service = services.OrderService()
        service.create(**serializer.validated_data, customer_id=customer_pk)

        return Response(
            data={"message": "Order Placed Successfully!"},
            status=status.HTTP_201_CREATED,
        )
    
    def get(self, request, **kwargs):
        query_params = serializers.OrderListQueryParametersSerializer(
            data=request.query_params
        )
        query_params.is_valid(raise_exception=True)

        selector = services.OrderSelector()
        orders = selector.order_list(**query_params.validated_data)

        paginator = OrderPagination()
        paginated_data = paginator.paginate_queryset(orders, request)

        serializer = serializers.DeliveryOrderListOutSerializer(
            paginated_data, many=True, context={"request": request}
        )

        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response


class CustomerOrderListView(APIView):
    permission_classes = [IsAuthenticated, CustomersOnly]

    def get(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Access to this resource is denied")

        query_params = serializers.OrderListQueryParametersSerializer(
            data=request.query_params
        )
        query_params.is_valid(raise_exception=True)

        selector = services.OrderSelector()
        orders = selector.order_list(
            customer_id=customer_pk, **query_params.validated_data
        ).prefetch_related("products")

        paginator = OrderPagination()
        paginated_data = paginator.paginate_queryset(orders, request)

        serializer = serializers.OrderOutSerializer(
            paginated_data, many=True, context={"request": request}
        )

        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response


class OrderDetailUpdateView(APIView):

    permission_classes = [IsAuthenticated, DeliveriesOnly]

    def get(self, request, **kwargs):
        order_pk = kwargs['pk']
        order = get_object_or_404(Order.objects.prefetch_related('products'), id=order_pk)
        data = serializers.DeliveryOrderOutSerializer(order, context={"request": request}).data
        return Response(data=data)
    

    def patch(self, request, **kwargs):
        order_pk = kwargs['pk']
        order = get_object_or_404(Order ,id=order_pk)
        serializer = serializers.OrderStatusInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = services.OrderService()
        service.update_status(order, serializer.validated_data["status"])

        return Response(
            data={"message": "Order Status Updated Successfully!"},
            status=status.HTTP_200_OK,
        )
