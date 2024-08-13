from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from common.api.permissions import DistributorsOnly, CustomersOnly
from .models import Store, PickupAddress
from .serializers import (
    StoreInputSerializer,
    StoreOutSerializer,
    PickupAddressInputSerializer,
    PickupAddressOutSerializer,
)
from .services import (
    StoreService,
    StoreSelector,
    PickupAddressService,
    PickupAddressSelector,
)


class StoreCreateListView(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]

    def get(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Permission Denied!")

        selector = StoreSelector()
        stores = selector.store_list(distributor_id=distributor_pk)
        stores = StoreOutSerializer(
            stores, many=True, context={"request": request}
        ).data
        data = {"stores": stores}
        return Response(data=data)

    def post(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Permission Denied!")

        serializer = StoreInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = StoreService()
        service.create_store(**serializer.validated_data, distributor_id=distributor_pk)

        return Response(
            data={"message": "Store Created"}, status=status.HTTP_201_CREATED
        )


class StoreDisplayUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, DistributorsOnly]

    def get(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Permission Denied!")

        store_pk = kwargs["store_pk"]
        store = get_object_or_404(Store, pk=store_pk)
        if store.distributor_id != distributor_pk:
            raise PermissionDenied("Permission Denied!")

        store = StoreOutSerializer(store, context={"request": request}).data
        return Response(data=store)

    def patch(self, request, **kwargs):
        distributor_pk = kwargs["pk"]
        if request.user.pk != distributor_pk:
            raise PermissionDenied("Permission Denied!")

        store_pk = kwargs["store_pk"]
        store = get_object_or_404(Store, pk=store_pk)
        if store.distributor_id != distributor_pk:
            raise PermissionDenied("Permission Denied!")
        serializer = StoreInputSerializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        service = StoreService()
        service.update_store(store, **serializer.validated_data)

        return Response(data={"message": "Store Updated"}, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        pass


class PickupAddressListCreate(APIView):
    permission_classes = [IsAuthenticated, CustomersOnly]

    def post(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied(
                "Customers can add addresses to just their own profiles!"
            )

        serializer = PickupAddressInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PickupAddressService()
        service.create_pickup_address(
            **serializer.validated_data, customer_id=customer_pk
        )

        return Response(
            data={"message": "Pickup Address added successfully"},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Items of another user")

        selector = PickupAddressSelector()
        pickup_addresses = selector.pickup_address_list(customer_id=customer_pk)
        pickup_addresses.prefetch_related("city")
        serializer = PickupAddressOutSerializer(
            instance=pickup_addresses, many=True, context={"request": request}
        )
        data = {"addresses": serializer.data}

        return Response(data=data, status=status.HTTP_200_OK)


class PickupAddressDetailView(APIView):
    permission_classes = [IsAuthenticated, CustomersOnly]

    def get(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access Pickup address")

        address_pk = kwargs["address_pk"]
        pickup_address = get_object_or_404(
            PickupAddress, pk=address_pk, customer_id=customer_pk
        )
        serializer = PickupAddressOutSerializer(
            instance=pickup_address, context={"request": request}
        )
        data = {"address": serializer.data}

        return Response(data=data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Item of another user")

        address_pk = kwargs["address_pk"]
        address = get_object_or_404(
            PickupAddress, pk=address_pk, customer_id=customer_pk
        )
        serializer = PickupAddressInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        service = PickupAddressService()
        service.update_pickup_address(address, **serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, **kwargs):
        customer_pk = kwargs["pk"]
        if request.user.pk != customer_pk:
            raise PermissionDenied("Can't access cart Item of another user")

        address_pk = kwargs["address_pk"]
        address = get_object_or_404(
            PickupAddress, pk=address_pk, customer_id=customer_pk
        )

        service = PickupAddressService()
        service.delete_pickup_address(address)

        return Response(status=status.HTTP_204_NO_CONTENT)
