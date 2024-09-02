from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from common.api.paginator import OrderPagination
from common.api.permissions import CustomersOnly
from . import serializers
from . import services


class OrderListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), CustomersOnly()]

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
