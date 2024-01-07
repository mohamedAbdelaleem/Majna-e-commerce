from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, PasswordChangeSerializer
from .permissions import IsSameUser


class UsersView(APIView):
    def post(self, request: Request) -> Response:
        user = UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save()

        if settings.REQUIRE_ACCOUNT_ACTIVATION:
            user.send_email_confirmation_email()

        return Response(status=status.HTTP_201_CREATED)


class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated, IsSameUser)

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data={"message": "Password changed successfully"})
