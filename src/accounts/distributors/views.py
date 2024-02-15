from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from common.api.permissions import DistributorsOnly
from brands.services import BrandSelector
from brands.serializers import BrandOutSerializer
from brands_applications.services import BrandApplicationSelector
from brands_applications.serializers import BrandApplicationListOutSerializer


class DistributorBrandListView(APIView):
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


class DistributorBrandApplicationListView(APIView):
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
