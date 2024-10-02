from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Customer
from products.models import Product


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.CharField(max_length=500)
    review_date = models.DateField(auto_now_add=True)
    order_date = models.DateField()
