from django.urls import path
from . import views

app_name = 'brand_applications'


urlpatterns = [
    path('', views.BrandsApplications().as_view(), name='brand_applications'),
    path('<int:pk>', views.BrandApplication().as_view(), name='brand_application')
]

