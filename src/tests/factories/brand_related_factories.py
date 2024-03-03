import factory
from brands.models import Brand, BrandDistributors
from brands_applications.models import BrandApplication
from tests.factories.auth_factories import faker

class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand
    
    name = factory.lazy_attribute(lambda _: faker.company())


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
    authorization_doc = factory.lazy_attribute(lambda _:faker.file_name(extension='pdf'))  
    identity_doc = factory.lazy_attribute(lambda _:faker.file_name(extension='pdf'))  
    request_date = factory.lazy_attribute(lambda _: faker.date_time_this_decade())

    status = 'inprogress'
