from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector
from addresses.models import Store
from brands.models import Brand
from accounts.models import Customer


class Category(models.Model):
    name = models.CharField(unique=True)

    def __str__(self) -> str:
        return self.name


class SubCategory(models.Model):
    name = models.CharField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField()
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    stores = models.ManyToManyField(Store, through="Inventory")

    class Meta:
        indexes = [
            GinIndex(
                SearchVector("name", "description", config="english"),
                name="search_vector_idx",
            ),
            models.Index(fields=['price'], name='price_idx')
        ]

    def __str__(self) -> str:
        return self.name


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
    img_url = models.CharField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='album_items')
    is_cover = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

class FavoriteItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "customer"], name="unique_favorite_item"
            )
        ]
