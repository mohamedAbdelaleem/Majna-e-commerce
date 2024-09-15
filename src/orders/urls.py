from django.urls import path
from . import views


app_name = "orders"

urlpatterns = [
    path("", views.OrderListCreateView().as_view(), name="orders"),
    path("<int:pk>", views.OrderDetailUpdateView().as_view(), name="order"),
    path("publisher-key", views.get_publisher_key, name="publisher_key"),
    path("webhook", views.webhook, name="success_payment_handler"),
]

