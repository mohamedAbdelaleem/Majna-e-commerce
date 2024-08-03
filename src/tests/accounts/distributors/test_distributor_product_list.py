from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.products_factories import ProductFactory, InventoryFactory, AlbumItemFactory
from tests.factories.store_factories import StoreFactory
from tests.factories.brand_related_factories import BrandFactory, BrandDistributorsFactory
import tests.factories.auth_factories as auth_factories


class DistributorProductListTests(APITestCase):
    
    @classmethod
    def setUpTestData(cls) -> None:
        auth_factories.create_groups()
        cls.distributor = auth_factories.create_distributor("distributor@test.com")
        
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.brand = BrandFactory.create()
        BrandDistributorsFactory.create(brand=cls.brand, distributor=cls.distributor)
        
        cls.product = ProductFactory.create()
        InventoryFactory.create(store=cls.store, product=cls.product)
        AlbumItemFactory.create(product=cls.product, is_cover=True)

        cls.url = reverse("distributors:products", kwargs={'pk':cls.distributor.pk})

    def test_unauthenticated_failure(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        customer = auth_factories.create_customer("customer@test.com")
        token = auth_factories.generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        reviewer = auth_factories.create_reviewer("reviewer@test.com")
        token = auth_factories.generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_distributor_failure(self):
        distributor = auth_factories.create_distributor("distributor2@test.com")
        token = auth_factories.generate_auth_token(distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_retrieve(self):
        token = auth_factories.generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
