from django.urls import path
import carts.views as carts_views

app_name = "customers"

urlpatterns = [
    path(
        "<int:pk>/cart-items",
        view=carts_views.CartItemListCreate().as_view(),
        name="cart_items",
    ),
    path(
        "<int:pk>/cart-items/<int:cart_item_pk>",
        view=carts_views.CartItemDetail().as_view(),
        name="cart_item",
    ),
    
]
