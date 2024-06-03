from django.urls import path
from . import views


app_name = 'brands'

urlpatterns = [
    path("", views.BrandListView.as_view(), name="brands"),
    path("<int:pk>", views.BrandDetailView.as_view(), name="brand"),
    path("<int:pk>/applications", views.BrandApplicationCreateView().as_view(), name="brand_applications"),
    # path("<int:pk>/distributors", views., name="brand_distributors"),
]
