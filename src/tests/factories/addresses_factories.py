import factory
from faker import Faker
from addresses.models import Governorate, City, PickupAddress

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



class PickupAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PickupAddress
    city = factory.SubFactory(CityFactory)
    address = factory.lazy_attribute(lambda _: faker.address())