from django.contrib.auth.models import Group, AbstractBaseUser
from django.contrib.auth import get_user_model
from knox.models import AuthToken
from accounts.models import Distributor, Customer


ROLES = ["Customer", "Distributor", "Reviewer", "Delivery"]

def create_groups() -> None:
    for role in ROLES:
        Group.objects.get_or_create(name=role)


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
    Create new user and assign the user to the Reviewers Group

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


def create_delivery(email="test@test.com", password='123') -> AbstractBaseUser:
    """
    Create new user and assign the user to the Delivery Group

    - Warnings: 
        - Change the default email if it used previously  
        - the group should already exists use create_groups() to create 
           the groups if you didn't 
    """
    group = Group.objects.get(name="Delivery")
    delivery = get_user_model().objects.create_user(email, password)
    delivery.groups.add(group)
    delivery.save()

    return delivery


def generate_all_users_except(role_name: str):
    """Generate users to be used within unauthorized failure tests"""
    create_groups()
    users = []
    for i, role in enumerate(ROLES):
        if role != role_name:
            function_name = f"create_{role.lower()}"
            user = globals()[function_name](email=f"test{i}@test.com")
            users.append(user)
    return users


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
