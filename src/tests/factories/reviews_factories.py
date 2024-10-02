import factory
from faker import Faker
from reviews.models import Review


faker = Faker()


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    rating = factory.lazy_attribute(lambda _: faker.random_int(min=1, max=5))
    content = "review content"