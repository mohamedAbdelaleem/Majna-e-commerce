from django.db import models
from django.core.validators import MinValueValidator
from products import models as product_models
from accounts import models as accounts_models


class CartItem(models.Model):
    product = models.ForeignKey(product_models.Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(accounts_models.Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "customer"], name="unique_cart_item"
            )
        ]
