import factory
from faker import Faker
from products import models
from tests.factories.brand_related_factories import BrandFactory

faker = Faker()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category

    name = factory.Sequence(lambda n: f"brand_{n}")


class SubCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SubCategory

    name = factory.Sequence(lambda n: f"brand_{n}")
    category = factory.SubFactory(CategoryFactory)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Product

    sub_category = factory.SubFactory(SubCategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    price = factory.lazy_attribute(lambda _: faker.random_number(digits=3))


class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Inventory

    product = factory.SubFactory(ProductFactory)
    # store is assigned manually
    quantity = factory.lazy_attribute(lambda _: faker.random_number(digits=3))


class AlbumItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AlbumItem

    img_url = factory.lazy_attribute(lambda _: faker.file_name(extension="png"))
    product = factory.SubFactory(ProductFactory)

class FavoriteItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FavoriteItem
    
    product = factory.SubFactory(ProductFactory)
