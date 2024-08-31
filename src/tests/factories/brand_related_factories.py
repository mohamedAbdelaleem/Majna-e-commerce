import factory
from faker import Faker
from brands.models import Brand, BrandDistributors
from brands_applications.models import BrandApplication

faker = Faker()

class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand
    
    name = factory.Sequence(lambda n: f"brand_{n}")


class BrandDistributorsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BrandDistributors
    
    brand = factory.SubFactory(Brand)
    authorize_date = factory.lazy_attribute(lambda _: faker.date_time_this_decade())


class BrandApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BrandApplication

    brand = factory.SubFactory(BrandFactory)
    # distributor = factory.SubFactory(DistributorFactory)
    authorization_doc = factory.django.FileField(filename="auth.pdf")
    identity_doc = factory.django.FileField(filename="identity.pdf")
    request_date = factory.lazy_attribute(lambda _: faker.date_time_this_decade())
