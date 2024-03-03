import factory
from faker import Faker
from stores.models import Store
from tests.factories.addresses_factories import CityFactory

faker = Faker()

class StoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Store
    
    city = factory.SubFactory(CityFactory)
    name = factory.lazy_attribute(lambda _: faker.company())
    address = factory.lazy_attribute(lambda _: faker.name())
