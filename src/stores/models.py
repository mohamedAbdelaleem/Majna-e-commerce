from django.db import models
from accounts.models import Distributor


class Governorate(models.Model):
    name = models.CharField(max_length=50)
    name_ar = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50)
    name_ar = models.CharField(max_length=50)
    governorate = models.ForeignKey(Governorate, on_delete=models.PROTECT, related_name="cities")

    def __str__(self) -> str:
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=100)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    address = models.CharField()
    creation_date = models.DateTimeField(auto_now_add=True)
