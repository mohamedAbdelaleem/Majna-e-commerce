from django.urls import path
from knox import views as knoxViews
from . import views

app_name = "accounts"

urlpatterns = [
    path('login', views.LoginView.as_view(), name="login"),
    path('signup', views.SignUpView.as_view(), name="signup"),
    path('logout', knoxViews.LogoutView.as_view(), name="logout"),
    path('logout-all', knoxViews.LogoutAllView.as_view(), name="logout_all"),
    path('password-change', views.ChangePasswordView.as_view(), name="change_password")
]
