from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import serializers
from accounts.utils import clean_email


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)

    def validate(self, data):
        data["email"] = clean_email(data["email"])
        password = data["password"]
        email = data["email"]
        try:
            user = get_user_model().objects.get(email=email)
            if not user.check_password(password):
                raise ValidationError("")
        except (ObjectDoesNotExist, ValidationError):
            raise serializers.ValidationError({"detail": "Invalid email or password"})

        data["user"] = user

        return data

    def save(self):
        return self.validated_data["user"]


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    re_new_password = serializers.CharField(max_length=128)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Wrong password!")
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as error:
            raise serializers.ValidationError(detail=error.messages)

        return value

    def validate(self, data):
        if data["new_password"] != data["re_new_password"]:
            raise serializers.ValidationError("new password mismatch")
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
