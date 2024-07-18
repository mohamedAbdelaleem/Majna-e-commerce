from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from products import models
from products import serializers


class SubCategoryListView(APIView):
    def get(self, request):
        categories = models.SubCategory.objects.all()
        serializer = serializers.SubCategoryOutSerializer(categories, many=True)
        return Response(
            data={"sub_categories": serializer.data}, status=status.HTTP_200_OK
        )

class SubCategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, **kwargs):
        sub_category_pk = kwargs["pk"]
        sub_category = get_object_or_404(models.SubCategory, pk=sub_category_pk)
        serializer = serializers.CategoryOutSerializer(sub_category)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


