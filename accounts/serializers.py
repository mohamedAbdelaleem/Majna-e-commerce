from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .utils import clean_email


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=get_user_model().objects.all(),
                message="invalid email!",
            )
        ]
    )

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

