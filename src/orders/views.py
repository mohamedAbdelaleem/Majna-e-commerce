import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
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
        intent = service.create(**serializer.validated_data, customer_id=customer_pk)

        return Response(
            data={
                "client_secret": intent["client_secret"],
                'dpm_checker_link': 'https://dashboard.stripe.com/settings/payment_methods/review?transaction_id={}'.format(intent['id'])},
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


@api_view(["POST"])
def webhook(request):
    event = None
    payload = request.body
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    if endpoint_secret:
        sig_header = request.headers.get('stripe-signature', None)
        stripe.api_key = settings.STRIPE_SECRET
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('Webhook signature verification failed.' + str(e))
            return Response({'success':False})

    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = int(payment_intent['metadata']['order_id'])
        service = services.OrderService()
        service.handle_payment_intent_succeeded(order_id)
    else:
        print('Unhandled event type {}'.format(event['type']))

    return Response({'success':True})


@api_view(["GET"])
def get_publisher_key(request):
    return Response({'publisher-key': settings.STRIPE_PUBLISHER})
