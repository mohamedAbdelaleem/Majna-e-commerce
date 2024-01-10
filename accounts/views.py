from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .serializers import (
    UserSerializer,
    PasswordChangeSerializer,
    EmailConfirmationSerializer,
)


class UsersView(APIView):
    def post(self, request: Request) -> Response:
        user = UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user = user.save()

        if settings.REQUIRE_ACCOUNT_ACTIVATION:
            user.send_email_confirmation_email()

        return Response(status=status.HTTP_201_CREATED)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        if kwargs["pk"] != request.user.pk:
            raise PermissionDenied("UnAuthorized user")

        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data={"message": "Password changed successfully"})


class EmailConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        serializer = EmailConfirmationSerializer(data=request.data, context={"pk": pk})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if user.email_confirmed:
            return Response(
                data={"message": "Conflict!"}, status=status.HTTP_409_CONFLICT
            )

        user.email_confirmed = True
        user.save()

        return Response(data={"message": "Email Confirmed Successfully!"})
