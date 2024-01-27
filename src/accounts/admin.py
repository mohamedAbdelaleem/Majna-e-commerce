from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Customer, Distributor
# Register your models here.

## anything for now..

admin.site.register(get_user_model())
admin.site.register(Customer)
admin.site.register(Distributor)