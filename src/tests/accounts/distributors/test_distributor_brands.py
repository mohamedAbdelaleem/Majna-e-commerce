from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from brands.services import BrandSelector
from tests.factories.brand_related_factories import (
    BrandFactory,
    BrandDistributorsFactory,
)
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_auth_token,
    create_groups,
)


class DistributorBrandListTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor(email="distributor@test.com")
        cls.token = generate_auth_token(user=cls.distributor.user)
        cls.brand = BrandFactory.create()
        cls.brand2 = BrandFactory.create()
        BrandDistributorsFactory.create(distributor=cls.distributor, brand=cls.brand)

        cls.url = reverse("distributors:brands", kwargs={"pk": cls.distributor.pk})

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthorized_user_failure(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_distributor_failure(self):
        customer = create_customer(email="customer@test.com")
        token = generate_auth_token(user=customer.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer(email="reviewer@test.com")
        token = generate_auth_token(user=reviewer)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_user_failure(self):
        distributor = create_distributor(email="distributor2@test.com")
        token = generate_auth_token(user=distributor.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_brands_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        selector = BrandSelector()
        distributor_brands = selector.brand_list(
            distributors__pk=self.distributor.pk
        ).values_list('id', flat=True)

        for brand in response.data:
            self.assertIn(brand['id'], distributor_brands)
