from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.store_factories import StoreFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_groups,
    create_reviewer,
    generate_auth_token,
)


class RetrieveStoresTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.distributor2 = create_distributor("distributor2@test.com")
        cls.token = generate_auth_token(cls.distributor.user)
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.store2 = StoreFactory.create(distributor=cls.distributor2)
        cls.url = reverse(
            "distributors:stores",
            kwargs={"pk": cls.distributor.pk},
        )

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthenticated_failure(self):
        self.client.credentials()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("stores", response.data)

    def test_non_distributor_failure(self):
        customer = create_customer("customer@test.com")
        token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("stores", response.data)

        reviewer = create_reviewer("reviewer@test.com")
        token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("stores", response.data)

    def test_not_same_distributor_failure(self):
        url = reverse("distributors:stores", kwargs={"pk": self.distributor2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("stores", response.data)

    def test_success_stores_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("stores", response.data)
        stores = response.data['stores']
        for store in stores:
            distributor_id = store['distributor_id']
            self.assertEqual(distributor_id, self.distributor.pk)

class RetrieveStoreTests(APITestCase):
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

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthenticated_failure(self):
        self.client.credentials()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_distributor_failure(self):
        customer = create_customer("customer@test.com")
        token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_distributor_failure(self):
        distributor = create_distributor("distributor2@test.com")
        url = reverse(
            "distributors:store",
            kwargs={"pk": distributor.pk, "store_pk": self.store.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_stores_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("message", response.data)
