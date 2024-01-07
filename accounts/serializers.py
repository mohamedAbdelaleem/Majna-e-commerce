from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Customer, Distributor
from .utils import clean_email


class UserSerializer(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField()
    role = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "password",
            "phone_num",
            "email_confirmed",
            "user_role",
            "role",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "email_confirmed": {"read_only": True},
        }

    def get_user_role(self, user_obj):
        role = None
        if user_obj.is_customer():
            role = "customer"
        elif user_obj.is_distributor():
            role = "distributor"

        return role

    def validate_role(self, value):
        roles = ("customer", "distributor")
        if value not in roles:
            raise serializers.ValidationError("Invalid role")
        return value

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
        
        role = validated_data.pop("role")
        user = get_user_model().objects.create_user(**validated_data)
        if role == "customer":
            Customer.objects.create_customer(user)
        elif role == "distributor":
            Distributor.objects.create_distributor(user)

        return user

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
            instance.save()
        return instance


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
