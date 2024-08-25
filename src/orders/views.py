from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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
