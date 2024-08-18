from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.store_factories import StoreFactory
from tests.factories.products_factories import (
    ProductFactory,
    AlbumItemFactory,
    InventoryFactory,
)
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_auth_token,
    create_groups,
)

class StoreDeleteTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product1 = ProductFactory.create()
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product1)
        cls.cover_image = AlbumItemFactory.create(product=cls.product1, is_cover=True)
        
        cls.unattached_store = StoreFactory.create(distributor=cls.distributor)
        
        cls.url = reverse(
            "distributors:store",
            kwargs={"pk": cls.distributor.pk, "store_pk": cls.unattached_store.pk},
        )
        
    
    def setUp(self) -> None:
        distributor_token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_distributor_failure(self):
        customer = create_customer("customer@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        url = reverse(
            "distributors:store",
            kwargs={"pk": customer.pk, "store_pk": self.unattached_store.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        url = reverse(
            "distributors:store",
            kwargs={"pk": reviewer.pk, "store_pk": self.unattached_store.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_not_same_distributor_failure(self):
        distributor = create_distributor("distributor2@test.com")
        distributor_token = generate_auth_token(distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unattached_store_delete_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_working_store_delete_failure(self):
        """Test delete a store contains products with total quantity more than zero."""
        url = reverse(
            "distributors:store",
            kwargs={"pk": self.distributor.pk, "store_pk": self.store.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_empty_store_delete_success(self):
        """Test delete a store contains products with total quantity equal zero"""
        store = StoreFactory.create(distributor=self.distributor)
        InventoryFactory.create(store=store, product=self.product1, quantity=0)
        url = reverse(
            "distributors:store",
            kwargs={"pk": self.distributor.pk, "store_pk": store.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
