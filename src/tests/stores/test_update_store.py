from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.addresses_factories import CityFactory
from tests.factories.store_factories import StoreFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_groups,
    create_reviewer,
    generate_auth_token,
)


class UpdateStoreTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.token = generate_auth_token(cls.distributor.user)
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.url = reverse(
            "distributors:store",
            kwargs={"pk": cls.distributor.pk, "store_pk": cls.store.pk},
        )
        city = CityFactory.create()
        cls.valid_update_data = {
            "city": city.id,
            "address": "some street",
        }

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthenticated_failure(self):
        self.client.credentials()

        response = self.client.patch(self.url, self.valid_update_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_distributor_failure(self):
        customer = create_customer("customer@test.com")
        token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.patch(self.url, self.valid_update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.patch(self.url, self.valid_update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_distributor_failure(self):
        distributor = create_distributor("distributor2@test.com")
        url = reverse(
            "distributors:store",
            kwargs={"pk": distributor.pk, "store_pk": self.store.pk},
        )
        response = self.client.patch(url, self.valid_update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_city_failure(self):
        data = self.valid_update_data
        data["city"] = data["city"] + 12

        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_store_update(self):
        response = self.client.patch(self.url, self.valid_update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
