from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .managers import CustomerManager, CustomUserManager, DistributorManager
from .utils import clean_email


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    phone_num = models.CharField(max_length=15, null=True)
    email_confirmed = models.BooleanField(default=False)

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

    def send_account_activation_email(self):
        subject = "Account Activation"
        activation_link = settings.ACTIVATION_LINK
        html_message = render_to_string(
            "account_activation.html", {"activation_link": activation_link}
        )
        text_message = strip_tags(html_message)

        send_mail(
            subject,
            text_message,
            from_email=None,
            recipient_list=[self.email],
            html_message=html_message,
        )

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
