import factory
from faker import Faker
from stores.models import Governorate, City


faker = Faker()

class GovernorateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Governorate
    
    name = factory.lazy_attribute(lambda _: faker.name())
    name_ar = factory.lazy_attribute(lambda _: faker.name())


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City
    
    governorate = factory.SubFactory(GovernorateFactory)
    name = factory.lazy_attribute(lambda _: faker.name())
    name_ar = factory.lazy_attribute(lambda _: faker.name())


