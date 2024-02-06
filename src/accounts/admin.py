from django.contrib import admin
from .models import Customer, Distributor
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser



## anything for now..

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_active', 'is_staff', 'is_customer', 'is_distributor', 'is_reviewer')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'phone_num', 'password', 'email_confirmed')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_num', 'password1', 'password2', 'email_confirmed'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(Customer)
admin.site.register(Distributor)