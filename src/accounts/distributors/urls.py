from django.urls import path
from . import views

app_name = "distributors"

urlpatterns = [
    path(
        "<int:pk>/brands",
        view=views.DistributorBrandListView().as_view(),
        name="brands",
    ),
    path(
        "<int:pk>/brands-applications",
        view=views.DistributorBrandApplicationListView().as_view(),
        name="brands_applications",
    ),
]
