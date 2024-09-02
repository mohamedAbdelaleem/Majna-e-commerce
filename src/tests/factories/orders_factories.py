import factory
from faker import Faker
from accounts.models import Customer
from addresses.models import PickupAddress, Store
from orders import models
from products.models import Product

faker = Faker()


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Order


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OrderItem

    unit_price = factory.lazy_attribute(lambda _: faker.random_number(digits=3))


class OrderItemStoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OrderItemStore


def create_test_order(
    customer: Customer,
    pickup_address: PickupAddress,
    product: Product,
    quantity: int,
    store: Store,
):
    order = OrderFactory.create(customer=customer, pickup_address=pickup_address)
    order_item = OrderItemFactory.create(product=product, order=order, quantity=quantity)
    OrderItemStoreFactory.create(
        order_item=order_item, store=store, reserved_quantity=quantity
    )
