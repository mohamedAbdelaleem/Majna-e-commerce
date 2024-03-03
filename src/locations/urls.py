from django.urls import path
from . import views


urlpatterns = [
    path("governorates",
         view=views.GovernorateListView().as_view(),
         name="governorates"),
]
