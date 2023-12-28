from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group



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
    
    def create_distributor(self, user, **extra_fields):
        new_distributor = self.model(user=user)
        new_distributor.save()
        distributor_group = Group.objects.get(name="Distributor")
        user.groups.add(distributor_group)
        user.save()
        return new_distributor
    
    
class CustomerManager(models.Manager):
    
    def create_customer(self, user, **extra_fields):
        new_customer = self.model(user=user)
        new_customer.save()
        customer_group = Group.objects.get(name="Customer")
        user.groups.add(customer_group)
        user.save()
        return new_customer
    