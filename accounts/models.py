from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomerManager, CustomUserManager, DistributorManager
from .utils import clean_email


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    phone_num = models.CharField(max_length=15, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def is_customer(self) -> bool:
        return self.groups.filter(name="Customer").exists()

    def is_distributor(self) -> bool:
        return self.groups.filter(name="Distributor").exists()

    def clean(self):
        super().clean()
        self.email = clean_email(self.email)

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class Customer(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.PROTECT, primary_key=True
    )  # diff

    objects = CustomerManager()


class Distributor(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.PROTECT, primary_key=True
    )

    objects = DistributorManager()
