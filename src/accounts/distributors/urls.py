from django.urls import path
import stores.views as stores_views
from . import views

app_name = "distributors"

urlpatterns = [
    path(
        "<int:pk>/brands",
        view=views.DistributorBrandsView().as_view(),
        name="brands",
    ),
    path(
        "<int:pk>/brands-applications",
        view=views.DistributorBrandApplicationsView().as_view(),
        name="brands_applications",
    ),
    path("<int:pk>/stores",
         view=stores_views.StoreCreateListView().as_view(),
         name="stores"),
    path("<int:pk>/stores/<int:store_pk>",
         view=stores_views.StoreDisplayUpdateDeleteView().as_view(),
         name="store"),
    path("<int:pk>/products",
         view=views.DistributorProductListView().as_view(),
         name="products"),
    path("<int:pk>/products/<int:product_pk>",
         view=views.ProductDetailUpdateDeleteView().as_view(),
         name="product"),
]
