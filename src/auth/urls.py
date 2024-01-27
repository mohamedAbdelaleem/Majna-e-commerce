from django.urls import path
from knox import views as knoxViews
from . import views

app_name = "auth"

urlpatterns = [
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", knoxViews.LogoutView.as_view(), name="logout"),
    path("logout-all", knoxViews.LogoutAllView.as_view(), name="logout_all"),

]
