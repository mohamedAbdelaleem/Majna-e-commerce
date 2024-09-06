from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.addresses_factories import CityFactory, GovernorateFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    generate_all_users_except,
    generate_auth_token,
    create_groups,
)


class AddressCreateTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.city = CityFactory.create()
        cls.governorate = GovernorateFactory.create()
        cls.customer = create_customer(email="customer@test.com")
        cls.token = generate_auth_token(cls.customer.user)
        cls.url = reverse("customers:addresses", kwargs={"pk": cls.customer.pk})
        cls.valid_data = {
            "city_id": cls.city.pk,
            "address": "Street 1 house number 3",
        }

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        users = generate_all_users_except("Customer")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
            url = reverse("customers:addresses", kwargs={"pk": user.pk})
            response = self.client.post(url, data=self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            
    def test_not_same_customer_failure(self):
        url = reverse("customers:addresses", kwargs={"pk": self.customer.pk + 1})
        response = self.client.post(url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_city_failure(self):
        data  = self.valid_data.copy()
        data["city_id"] = self.city.pk + 100
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_add(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

