from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .utils import clean_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "password",
            "phone_num",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        """Validate the insensitivity of the email address"""
        email = clean_email(value)
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError("invalid credentials!")
        return email

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(detail=e.messages)

        return value

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
    

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        instance.set_password(validated_data["password"])
        instance.save()
        return instance



class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    re_new_password = serializers.CharField(max_length=128)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Wrong password!")
        return value

    def validate(self, data):
        if data["new_password"] != data["re_new_password"]:
            raise serializers.ValidationError("new password mismatch")
        return data
