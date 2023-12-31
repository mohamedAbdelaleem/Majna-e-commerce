from django.contrib.auth.signals import user_logged_in
from django.utils import timezone

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from knox.views import LoginView as knoxLoginView
from knox.models import AuthToken

from .serializers import UserSerializer, ChangePasswordSerializer, LoginSerializer
from .models import Customer, Distributor


class LoginView(knoxLoginView):

    permission_classes = (AllowAny,)

    def get_post_response_data(self, user, token, instance):
        UserSerializer = self.get_user_serializer_class()

        data = {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'token': token
        }
        if UserSerializer is not None:
            data["user"] = UserSerializer(
                user
            ).data
        
        role = ""
        if user.is_customer():
            role = "customer"
        elif user.is_distributor():
            role = "distributor"
        
        data["role"] = role

        return data
    
    def post(self, request):

        credentials = LoginSerializer(data=request.data)
        credentials.is_valid(raise_exception=True)
        user = credentials.save()
        
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )
        token_ttl = self.get_token_ttl()
        instance, token = AuthToken.objects.create(user, token_ttl)
        user_logged_in.send(sender=user.__class__,
                            request=request, user=user)
        data = self.get_post_response_data(user, token, instance)
        return Response(data)


class SignUpView(APIView):
    
    def post(self, request: Request) -> Response:
        
        user = UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)

        try:
            role = request.data["role"].lower()
        except KeyError:
            raise serializers.ValidationError(detail="role attribute is required")
        
        if role == "customer":
            user = user.save()
            Customer.objects.create_customer(user=user)
        elif role == "distributor":
            user = user.save()
            Distributor.objects.create_distributor(user=user)
        else:
            raise serializers.ValidationError(detail="role is invalid")

        return Response(status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        request_data = ChangePasswordSerializer(data=request.data, context={"request":request})
        request_data.is_valid(raise_exception=True)
        new_password = request_data.validated_data["new_password"]

        user = UserSerializer(request.user, data={"password":new_password}, partial=True)
        user.is_valid(raise_exception=True)
        user.save()

        return Response()

