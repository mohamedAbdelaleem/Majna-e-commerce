from django.urls import path
from . import views

app_name = 'brand_applications'


urlpatterns = [
    path('', views.BrandApplicationListView().as_view(), name='brand_applications'),
    path('<int:pk>', views.BrandApplicationDetailUpdateView().as_view(), name='brand_application')
]

