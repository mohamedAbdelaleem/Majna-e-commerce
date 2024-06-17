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
    generate_auth_token,
    create_groups,
)


class ProductListTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("products:products")
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product1 = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product1)
        cls.cover_image = AlbumItemFactory.create(product=cls.product1, is_cover=True)

    def test_unauthenticated_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_role_independent(self):
        distributor_token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        customer = create_customer("customer@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_full_text_search(self):
        response = self.client.get(
            self.url, QUERY_STRING="search=samsung+phone"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_invalid_ordering(self):
        response = self.client.get(
            self.url, QUERY_STRING="ordering=category_id"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_price_range(self):
        response = self.client.get(
            self.url, QUERY_STRING="price__range=100, 1000, 300"
        )  # it must be 2 values
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            self.url, QUERY_STRING="price__range=100"
        )  # it must be 2 values
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(self.url, QUERY_STRING="price__range=-100, 1000")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CategoryProductListTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product1 = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        cls.product2 = ProductFactory.create(
            name="Redmi new phone", description="New phone From Redmi"
        )
        cls.category_id1 = cls.product1.sub_category.category_id
        cls.category_id2 = cls.product2.sub_category.category_id
        cls.url = reverse("products:category_products", kwargs={'pk':cls.category_id1})
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product1)
        cls.cover_image = AlbumItemFactory.create(product=cls.product1, is_cover=True)

    def test_unauthenticated_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_not_found_failure(self):
        url = reverse("products:category_products", kwargs={'pk':self.category_id2+2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_return_category_products(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 1)

    def test_role_independent(self):
        distributor_token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        customer = create_customer("customer@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_full_text_search(self):
        response = self.client.get(
            self.url, QUERY_STRING="search=samsung+phone"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_invalid_ordering(self):
        response = self.client.get(
            self.url, QUERY_STRING="ordering=category_id"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_price_range(self):
        response = self.client.get(
            self.url, QUERY_STRING="price__range=100, 1000, 300"
        )  # it must be 2 values
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            self.url, QUERY_STRING="price__range=100"
        )  # it must be 2 values
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(self.url, QUERY_STRING="price__range=-100, 1000")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)