from django.urls import path
import carts.views as carts_views
import products.views as products_views
from addresses import views as addresses_views
from orders import views as orders_views

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
    path(
        "<int:pk>/favorite-items",
        view=products_views.FavoriteItemListCreate().as_view(),
        name="favorite_items",
    ),
    path(
        "<int:pk>/favorite-items/<int:favorite_item_pk>",
        view=products_views.FavoriteItemDelete().as_view(),
        name="favorite_item",
    ),
    path(
        "<int:pk>/addresses",
        view=addresses_views.PickupAddressListCreate().as_view(),
        name="addresses",
    ),
    path(
        "<int:pk>/addresses/<int:address_pk>",
        view=addresses_views.PickupAddressDetailView().as_view(),
        name="address",
    ),
    
    path(
        "<int:pk>/orders",
        view=orders_views.CustomerOrderListView().as_view(),
        name="orders",
    ),
]
