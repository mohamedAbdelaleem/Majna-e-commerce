import factory
from faker import Faker
from carts import models as carts_models
from tests.factories.products_factories import ProductFactory

faker = Faker()


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = carts_models.CartItem

    product = factory.SubFactory(ProductFactory)
    quantity = factory.lazy_attribute(lambda _: faker.random_number(digits=2))
