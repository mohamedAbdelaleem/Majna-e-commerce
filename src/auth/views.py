from django.contrib.auth.signals import user_logged_in
from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from knox.views import LoginView as knoxLoginView
from knox.models import AuthToken

from .serializers import PasswordChangeSerializer, LoginSerializer


class LoginView(knoxLoginView):
    permission_classes = (AllowAny,)

    def get_post_response_data(self, user, token, instance):
        UserSerializer = self.get_user_serializer_class()

        data = {"expiry": self.format_expiry_datetime(instance.expiry), "token": token}
        if UserSerializer is not None:
            data["user"] = UserSerializer(user).data

        return data

    def post(self, request):
        credentials = LoginSerializer(data=request.data)
        credentials.is_valid(raise_exception=True)
        user = credentials.save()
        if not user.email_confirmed:
            raise PermissionDenied("Unconfirmed email address!")
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        token_ttl = self.get_token_ttl()
        instance, token = AuthToken.objects.create(user, token_ttl)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        data = self.get_post_response_data(user, token, instance)
        return Response(data)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data={"message": "Password changed successfully"})
