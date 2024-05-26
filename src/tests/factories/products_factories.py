import factory
from faker import Faker
from products import models
from tests.factories.store_factories import StoreFactory

faker = Faker()

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category

class SubCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SubCategory
    category = factory.SubFactory(CategoryFactory)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Product
    sub_category = factory.SubFactory(SubCategoryFactory)
    store = factory.SubFactory(StoreFactory)

class AlbumItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AlbumItem
    img_url = factory.lazy_attribute(lambda _: faker.file_name(extension='png'))
    product = factory.SubFactory(ProductFactory)