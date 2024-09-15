from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product
from accounts.models import Customer
from addresses.models import PickupAddress, Store


ORDER_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("placed", "Placed"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
]


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, through="OrderItem")
    pickup_address = models.ForeignKey(PickupAddress, on_delete=models.PROTECT)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, default="pending", max_length=12)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order #{self.pk}"

    class Meta:
        indexes = [
            models.Index(fields=['status'], name='status_idx')
        ]

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.SmallIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(1)]
    )
    stores = models.ManyToManyField(Store, through='OrderItemStore')

    def __str__(self) -> str:
        return f"Oder #{self.pk} Item"


class OrderItemStore(models.Model):
    """A Product can be available in multiple stores and the quantity requested
        within an order item may fulfilled by more than one store"""
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    reserved_quantity = models.SmallIntegerField(validators=[MinValueValidator(1)])
