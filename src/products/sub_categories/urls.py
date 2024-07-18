from django.urls import path
from . import views

app_name = "sub_categories"

urlpatterns = [
    
    path(
        "", views.SubCategoryListView().as_view(), name="sub_categories"
    ),
    path(
        "<int:pk>", views.SubCategoryDetailView().as_view(), name="sub_category"
    ),
]
