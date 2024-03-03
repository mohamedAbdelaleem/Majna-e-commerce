from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from common.api.permissions import DistributorsOnly
from .models import Store
from .serializers import StoreInputSerializer, StoreOutSerializer
from .services import StoreService, StoreSelector


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
