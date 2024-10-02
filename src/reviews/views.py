from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from common.api.paginator import PagePagination
from common.api.permissions import CustomersOnly
from . import models
from . import serializers
from . import services


class ReviewListCreate(APIView):
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), CustomersOnly()]

    def post(self, request, **kwargs):
        product_pk = kwargs["pk"]
        customer_pk = request.user.pk
        product = get_object_or_404(models.Product, pk=product_pk)

        serializer = serializers.ReviewInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = services.ReviewService()
        service.create(product.pk, customer_pk, **serializer.validated_data)
        
        return Response(
            data={"message": "Review added successfully"},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, **kwargs):
        product_pk = kwargs["pk"]
        product = get_object_or_404(models.Product, pk=product_pk)

        selector = services.ReviewSelector()
        reviews = selector.review_list(product_id=product.pk)
        paginator = PagePagination()
        paginated_data = paginator.paginate_queryset(reviews, request)

        serializer = serializers.ReviewOutputSerializer(paginated_data, many=True)
        response = paginator.get_paginated_response(serializer.data)

        return response
    

class ReviewUpdateDetailDelete(APIView):
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), CustomersOnly()]

    def patch(self, request, **kwargs):
        product_pk = kwargs["pk"]
        customer_pk = request.user.pk
        review_pk = kwargs["review_pk"]
        review = get_object_or_404(models.Review, pk=review_pk, product_id=product_pk)
        if review.customer_id != customer_pk:
            raise PermissionDenied("Can't access this resource")

        serializer = serializers.ReviewInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        service = services.ReviewService()
        service.update(review, **serializer.validated_data)
        
        return Response(
            data={"message": "Review updated successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def get(self, request, **kwargs):
        product_pk = kwargs["pk"]
        review_pk = kwargs["review_pk"]
        review = get_object_or_404(models.Review, pk=review_pk, product_id=product_pk)

        serializer = serializers.ReviewOutputSerializer(review)

        return Response(data=serializer.data)
    
    def delete(self, request, **kwargs):
        product_pk = kwargs["pk"]
        customer_pk = request.user.pk
        review_pk = kwargs["review_pk"]
        review = get_object_or_404(models.Review, pk=review_pk, product_id=product_pk)
        if review.customer_id != customer_pk:
            raise PermissionDenied("Can't access this resource")

        service = services.ReviewService()
        service.delete(review)
        
        return Response(
            data={"message": "Review deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )