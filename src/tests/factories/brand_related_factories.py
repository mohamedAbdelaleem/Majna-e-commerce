import factory
from brands.models import Brand
from brands_applications.models import BrandApplication
from utils.tests import faker

class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand
    
    name = factory.lazy_attribute(lambda _: faker.company())



# class DistributorFactory(factory.DjangoModelFactory):
#     class Meta:
#         model = Distributor

#     name = factory.Faker('company')

class BrandApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BrandApplication

    brand = factory.SubFactory(BrandFactory)
    # distributor = factory.SubFactory(DistributorFactory)
    authorization_doc = factory.lazy_attribute(lambda _:faker.file_name(extension='pdf'))  
    identity_doc = factory.lazy_attribute(lambda _:faker.file_name(extension='pdf'))  
    request_date = factory.lazy_attribute(lambda _: faker.date_time_this_decade())

    status = 'inprogress'
