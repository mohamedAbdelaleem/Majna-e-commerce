from django.urls import path
from . import views


app_name = "orders"

urlpatterns = [
    path("", views.OrderListCreateView().as_view(), name="orders"),
    path("<int:pk>", views.OrderDetailUpdateView().as_view(), name="order"),
]

