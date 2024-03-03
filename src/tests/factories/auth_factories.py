from django.contrib.auth.models import Group, AbstractBaseUser
from django.contrib.auth import get_user_model
from knox.models import AuthToken
from accounts.models import Distributor, Customer


def create_groups() -> None:
    Group.objects.get_or_create(name="Customer")
    Group.objects.get_or_create(name="Distributor")
    Group.objects.get_or_create(name="Reviewer")


def create_distributor(email="test@test.com", password='123') -> Distributor:
    """
    Create new user and assign the user to the Distributor Group

    - Warnings: 
        - Change the default email if it used previously  
        - the group should already exists use create_groups() to create 
           the groups if you didn't 
    """
    user = get_user_model().objects.create_user(email, password)
    distributor = Distributor.objects.create_distributor(user=user)

    return distributor


def create_customer(email="test@test.com", password='123') -> Customer:
    """
    Create new user and assign the user to the Customer Group

    - Warnings: 
        - Change the default email if it used previously  
        - the group should already exists use create_groups() to create 
           the groups if you didn't 
    """
    user = get_user_model().objects.create_user(email, password)
    customer = Customer.objects.create_customer(user=user)

    return customer

def create_reviewer(email="test@test.com", password='123') -> AbstractBaseUser:
    """
    Create new user and assign the user to the Customers Group

    - Warnings: 
        - Change the default email if it used previously  
        - the group should already exists use create_groups() to create 
           the groups if you didn't 
    """
    group = Group.objects.get(name="Reviewer")
    reviewer = get_user_model().objects.create_user(email, password)
    reviewer.groups.add(group)
    reviewer.save()

    return reviewer


def create_normal_user(email="test@test.com", password='123') -> AbstractBaseUser:
    """
    Create new user without assigning the user to the any Group

    - Warnings: 
        - Change the default email if it used previously  
        - the group should already exists use create_groups() to create 
           the groups if you didn't 
    """
    user = get_user_model().objects.create_user(email, password)
    return user

def generate_auth_token(user: AbstractBaseUser) -> AuthToken:

    _, token = AuthToken.objects.create(user=user)
    return token
