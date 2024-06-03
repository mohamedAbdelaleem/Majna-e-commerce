from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.api.permissions import ReviewersOnly
from common.api.paginator import paginator
from .models import BrandApplication as BrandApplicationModel
from .services import BrandApplicationSelector, BrandApplicationService
from .serializers import (
    BrandApplicationOutSerializer,
    BrandApplicationStatusSerializer,
    BrandApplicationListOutSerializer,
)


class BrandApplicationListView(APIView):
    permission_classes = [IsAuthenticated, ReviewersOnly]

    def get(self, request):
        selector = BrandApplicationSelector()
        applications = selector.brand_application_list(status="inprogress")

        data = paginator.paginate_queryset(applications, request)
        data = BrandApplicationListOutSerializer(
            data, many=True, context={"request": request}
        ).data

        paginated_response = paginator.get_paginated_response(data)

        return paginated_response


class BrandApplicationDetailUpdateView(APIView):
    permission_classes = [IsAuthenticated, ReviewersOnly]

    def get(self, request, **kwargs):
        application = get_object_or_404(BrandApplicationModel, pk=kwargs["pk"])

        data = BrandApplicationOutSerializer(
            application, context={"request": request}
        ).data

        return Response(data)

    def patch(self, request, **kwargs):
        application = get_object_or_404(BrandApplicationModel, pk=kwargs["pk"])

        serializer = BrandApplicationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status = serializer.validated_data["status"]

        service = BrandApplicationService()
        service.update_status(application, status)

        return Response(
            data={"message": "Brand Application Status Updated Successfully"}
        )
