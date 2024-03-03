from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from stores.models import Store
from tests.factories.addresses_factories import CityFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_groups,
    create_reviewer,
    generate_auth_token
)


class AddStoreTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.token = generate_auth_token(cls.distributor.user)
        cls.url = reverse("distributors:stores", kwargs={'pk':cls.distributor.pk})
        city = CityFactory.create()
        cls.valid_data = {
            "city": city.id,
            "name": "store name",
            "address": "some street",
        }

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
    

    def test_unauthenticated_failure(self):
        stores_count = Store.objects.count()
        self.client.credentials()

        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        curr_stores_count = Store.objects.count()
        self.assertEqual(stores_count, curr_stores_count)

    def test_non_distributor_failure(self):
        stores_count = Store.objects.count()
        customer = create_customer("customer@test.com")
        token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        curr_stores_count = Store.objects.count()
        self.assertEqual(stores_count, curr_stores_count)

        reviewer = create_reviewer("reviewer@test.com")
        token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        curr_stores_count = Store.objects.count()
        self.assertEqual(stores_count, curr_stores_count)

    def test_not_same_distributor_failure(self):
        stores_count = Store.objects.count()

        distributor = create_distributor("distributor2@test.com")
        url = reverse("distributors:stores", kwargs={'pk':distributor.pk})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        curr_stores_count = Store.objects.count()
        self.assertEqual(stores_count, curr_stores_count)

    def test_invalid_city_failure(self):
        stores_count = Store.objects.count()
        data = self.valid_data
        data["city"] = data["city"] + 12
        
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        curr_stores_count = Store.objects.count()
        self.assertEqual(stores_count, curr_stores_count)
    
    def test_success_store_creation(self):
        stores_count = Store.objects.count()

        response = self.client.post(self.url, self.valid_data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        curr_stores_count = Store.objects.count()
        self.assertEqual(stores_count, curr_stores_count-1)

