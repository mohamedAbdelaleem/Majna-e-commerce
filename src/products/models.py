from django.db import models
from django.core.validators import MinValueValidator
from stores.models import Store
from brands.models import Brand
from common.validators import validate_max_filename_length


class Category(models.Model):
    name = models.CharField()

    def __str__(self) -> str:
        return self.name


class SubCategory(models.Model):
    name = models.CharField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    title = models.CharField()
    description = models.TextField()
    price = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    stores = models.ManyToManyField(Store, through="Inventory")

    def __str__(self) -> str:
        return self.title


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "store"], name="unique_inventory"
            )
        ]


class AlbumItem(models.Model):
    img_url = models.CharField(validators=[validate_max_filename_length])
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_cover = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
