import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.products_factories import (
    ProductFactory,
    InventoryFactory,
    AlbumItemFactory,
)
from tests.factories.store_factories import StoreFactory
from tests.factories.brand_related_factories import (
    BrandFactory,
    BrandDistributorsFactory,
)
import tests.factories.auth_factories as auth_factories


class ProductUpdateTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        auth_factories.create_groups()
        cls.distributor = auth_factories.create_distributor("distributor@test.com")
        cls.distributor2 = auth_factories.create_distributor("distributor2@test.com")

        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.store2 = StoreFactory.create(distributor=cls.distributor2)
        cls.brand = BrandFactory.create()
        BrandDistributorsFactory.create(brand=cls.brand, distributor=cls.distributor)

        cls.product = ProductFactory.create(name="name", description="description")
        InventoryFactory.create(store=cls.store, product=cls.product)
        AlbumItemFactory.create(product=cls.product, is_cover=True)

        cls.url = reverse(
            "distributors:product",
            kwargs={"pk": cls.distributor.pk, "product_pk": cls.product.pk},
        )
        cls.data = {
            "name": "name",
            "description": "description",
            "price": 12.3,
            "inventory": [
                {"store_pk": cls.store.pk, "quantity": 3},
            ],
        }
        cls.json_data = json.dumps(cls.data)

    def setUp(self) -> None:
        token = auth_factories.generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.patch(self.url, self.json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        customer = auth_factories.create_customer("customer@test.com")
        token = auth_factories.generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.patch(self.url, self.json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = auth_factories.create_reviewer("reviewer@test.com")
        token = auth_factories.generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.patch(self.url, self.json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_distributor_failure(self):
        token = auth_factories.generate_auth_token(self.distributor2.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.patch(self.url, self.json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_owned_product_failure(self):
        BrandDistributorsFactory.create(brand=self.brand, distributor=self.distributor2)

        product = ProductFactory.create()
        InventoryFactory.create(store=self.store2, product=product)
        AlbumItemFactory.create(product=product, is_cover=True)
        url = reverse(
            "distributors:product",
            kwargs={"pk": self.distributor.pk, "product_pk": product.pk},
        )
        response = self.client.patch(url, self.json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_not_found(self):
        url = reverse(
            "distributors:product",
            kwargs={"pk": self.distributor.pk, "product_pk": self.product.pk + 3},
        )
        response = self.client.patch(url, self.json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_store(self):
        data = self.data.copy()
        data["inventory"] = [{"store_pk": self.store2.pk, "quantity": 3}]
        json_data = json.dumps(data)
        response = self.client.patch(self.url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_values_failure(self):
        data = self.data.copy()
        data["price"] = -1
        json_data = json.dumps(data)
        response = self.client.patch(self.url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["price"] = 12
        data["inventory"][0]["quantity"] = -1
        json_data = json.dumps(data)
        response = self.client.patch(self.url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_empty_inventory_failure(self):
        data = {"inventory": []}
        json_data = json.dumps(data)
        response = self.client.patch(self.url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_update(self):
        response = self.client.patch(self.url, self.json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_partial_update(self):
        data = {"name": "New name"}
        json_data = json.dumps(data)
        response = self.client.patch(self.url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)



class ProductDeleteTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        auth_factories.create_groups()
        cls.distributor = auth_factories.create_distributor("distributor@test.com")
        cls.distributor2 = auth_factories.create_distributor("distributor2@test.com")

        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.store2 = StoreFactory.create(distributor=cls.distributor2)
        cls.brand = BrandFactory.create()
        BrandDistributorsFactory.create(brand=cls.brand, distributor=cls.distributor)

        cls.product = ProductFactory.create()
        InventoryFactory.create(store=cls.store, product=cls.product)
        AlbumItemFactory.create(product=cls.product, is_cover=True)

        cls.url = reverse(
            "distributors:product",
            kwargs={"pk": cls.distributor.pk, "product_pk": cls.product.pk},
        )
    
    def setUp(self) -> None:
        token = auth_factories.generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        customer = auth_factories.create_customer("customer@test.com")
        token = auth_factories.generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = auth_factories.create_reviewer("reviewer@test.com")
        token = auth_factories.generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_distributor_failure(self):
        token = auth_factories.generate_auth_token(self.distributor2.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_owned_product_failure(self):
        BrandDistributorsFactory.create(brand=self.brand, distributor=self.distributor2)

        product = ProductFactory.create()
        InventoryFactory.create(store=self.store2, product=product)
        AlbumItemFactory.create(product=product, is_cover=True)
        url = reverse(
            "distributors:product",
            kwargs={"pk": self.distributor.pk, "product_pk": product.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_not_found(self):
        url = reverse(
            "distributors:product",
            kwargs={"pk": self.distributor.pk, "product_pk": self.product.pk + 3},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_success_delete(self):
        token = auth_factories.generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
