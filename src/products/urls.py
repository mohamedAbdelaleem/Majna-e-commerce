from django.urls import path
from reviews import views as reviews_views
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListCreateView().as_view(), name="products"),
    path("<int:pk>", views.ProductDetailView().as_view(), name="product"),
    path(
        "<int:pk>/album-items",
        views.AlbumItemListCreate().as_view(),
        name="album_items",
    ),
    path(
        "<int:pk>/album-items/<int:album_item_pk>",
        views.AlbumItemDetailUpdateDeleteView().as_view(),
        name="album_item",
    ),
    path(
        "<int:pk>/reviews", reviews_views.ReviewListCreate().as_view(), name="reviews"
    ),
    path(
        "<int:pk>/reviews/<int:review_pk>",
        reviews_views.ReviewUpdateDetailDelete().as_view(),
        name="review",
    ),
]
