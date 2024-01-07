from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.UsersView.as_view(), name="users"),
    path("<int:pk>/password-change", views.PasswordChangeView.as_view(), name="change_password"),

]
