from django.urls import path
from . import views


app_name = 'brands'

urlpatterns = [
    path("", views.BrandsView.as_view(), name="brands"),
    path("<int:pk>/applications", views.BrandApplications().as_view(), name="brand_applications"),
    # path("<int:pk>/distributors", views., name="brand_distributors"),
]
