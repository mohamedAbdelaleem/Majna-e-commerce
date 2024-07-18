from django.urls import path
from . import views

app_name = "categories"

urlpatterns = [
    
    path("", views.CategoryListView().as_view(), name="categories"),
    path(
        "<int:pk>", views.CategoryDetailView().as_view(), name="category"
    ),
    path(
        "<int:pk>/products",
        views.CategoryProductListView().as_view(),
        name="category_products",
    ),
]
