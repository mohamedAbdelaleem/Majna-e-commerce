from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model



class CustomUserManager(BaseUserManager):
    
    def _create_user(self, email: str, password: str, **extra_fields):
        
        if not email:
            raise ValueError("Email field must be set")
        
        user = self.model(email=email, password=password, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_user(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_staff(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)
    
    
class DistributorManager(models.Manager):
    
    def create_distributor_user(self, email, password, **extra_fields):
        new_user = get_user_model().objects.create_user(email, password, **extra_fields)
        new_distributor = self.model(user=new_user)
        return new_distributor
    
    
class CustomerManager(models.Manager):
    
    def create_customer_user(self, email, password, **extra_fields):
        new_user = get_user_model().objects.create_user(email, password, **extra_fields)
        new_customer = self.model(user=new_user)
        return new_customer
    