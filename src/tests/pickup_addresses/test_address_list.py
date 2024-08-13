from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.addresses_factories import PickupAddressFactory, CityFactory
import tests.factories.auth_factories as auth_factories


class PickupAddressListTests(APITestCase):
    
    @classmethod
    def setUpTestData(cls) -> None:
        auth_factories.create_groups()
        cls.customer = auth_factories.create_customer("customer@test.com")
        cls.customer2 = auth_factories.create_customer("customer2@test.com")
        cls.city = CityFactory.create()
        cls.address1 = PickupAddressFactory.create(city=cls.city, customer=cls.customer)
        cls.address2 = PickupAddressFactory.create(city=cls.city, customer=cls.customer2)

        cls.url = reverse("customers:addresses", kwargs={'pk':cls.customer.pk})

    def test_unauthenticated_failure(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        distributor = auth_factories.create_distributor("distributor@test.com")
        token = auth_factories.generate_auth_token(distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        reviewer = auth_factories.create_reviewer("reviewer@test.com")
        token = auth_factories.generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_customer_failure(self):
        token = auth_factories.generate_auth_token(self.customer2.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_retrieve(self):
        token = auth_factories.generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieved_carts_count(self):
        customer_token = auth_factories.generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['addresses']), 1)
