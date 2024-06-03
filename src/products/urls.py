from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListCreateView().as_view(), name="products"),

    path("/categories", views.CategoryListView().as_view(), name="categories"),
    path(
        "/sub-categories", views.SubCategoryListView().as_view(), name="sub_categories"
    ),
]
