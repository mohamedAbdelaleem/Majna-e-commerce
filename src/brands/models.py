from django.db import models
from accounts.models import Distributor


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    distributors = models.ManyToManyField(
        Distributor,
        through="BrandDistributors",
        through_fields=("brand", "distributor"),
    )

    def __str__(self) -> str:
        return self.name


class BrandDistributors(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    authorize_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint("brand", "distributor", name="brands_distributors"),
        ]

