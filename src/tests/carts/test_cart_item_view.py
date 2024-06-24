from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.store_factories import StoreFactory
from tests.factories.products_factories import (
    ProductFactory,
    AlbumItemFactory,
    InventoryFactory,
)
from tests.factories.carts_factories import CartItemFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_auth_token,
    create_groups,
)


class CartItemRetrieveTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product1 = ProductFactory.create()
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product1)
        cls.cover_image = AlbumItemFactory.create(product=cls.product1, is_cover=True)
        cls.customer = create_customer("customer@test.com")
        cls.cart_item = CartItemFactory.create(
            customer=cls.customer, product=cls.product1
        )
        cls.url = reverse(
            "customers:cart_item",
            kwargs={"pk": cls.customer.pk, "cart_item_pk": cls.cart_item.pk},
        )

    def test_unauthenticated_failure(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_customer_failure(self):
        distributor_token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": self.distributor.pk, "cart_item_pk": self.cart_item.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": reviewer.pk, "cart_item_pk": self.cart_item.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_success(self):
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_same_customer_failure(self):
        customer = create_customer("customer2@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_cart_item_not_exist_failure(self):
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        customer2 = create_customer("customer2@test.com")
        cart_item = CartItemFactory.create(
            customer=customer2, product=self.product1
        )
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": self.customer.pk, "cart_item_pk": cart_item.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CartItemUpdateTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product1 = ProductFactory.create()
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product1)
        cls.cover_image = AlbumItemFactory.create(product=cls.product1, is_cover=True)
        cls.customer = create_customer("customer@test.com")
        cls.cart_item = CartItemFactory.create(
            customer=cls.customer, product=cls.product1
        )
        cls.url = reverse(
            "customers:cart_item",
            kwargs={"pk": cls.customer.pk, "cart_item_pk": cls.cart_item.pk},
        )
        cls.data = {'quantity': 3}
    
    def setUp(self) -> None:
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_customer_failure(self):
        distributor_token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": self.distributor.pk, "cart_item_pk": self.cart_item.pk},
        )
        response = self.client.patch(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": reviewer.pk, "cart_item_pk": self.cart_item.pk},
        )
        response = self.client.patch(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_success(self):
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_not_same_customer_failure(self):
        customer = create_customer("customer2@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cart_item_not_exist_failure(self):
        customer2 = create_customer("customer2@test.com")
        cart_item = CartItemFactory.create(
            customer=customer2, product=self.product1
        )
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": self.customer.pk, "cart_item_pk": cart_item.pk},
        )
        response = self.client.patch(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_quantity_failure(self):
        data = {"quantity": 0}
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"quantity": -2}
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CartItemDeleteTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product1 = ProductFactory.create()
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product1)
        cls.cover_image = AlbumItemFactory.create(product=cls.product1, is_cover=True)
        cls.customer = create_customer("customer@test.com")
        cls.cart_item = CartItemFactory.create(
            customer=cls.customer, product=cls.product1
        )
        cls.url = reverse(
            "customers:cart_item",
            kwargs={"pk": cls.customer.pk, "cart_item_pk": cls.cart_item.pk},
        )
        
    
    def setUp(self) -> None:
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_customer_failure(self):
        distributor_token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": self.distributor.pk, "cart_item_pk": self.cart_item.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": reviewer.pk, "cart_item_pk": self.cart_item.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_not_same_customer_failure(self):
        customer = create_customer("customer2@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cart_item_not_exist_failure(self):
        customer2 = create_customer("customer2@test.com")
        cart_item = CartItemFactory.create(
            customer=customer2, product=self.product1
        )
        url = reverse(
            "customers:cart_item",
            kwargs={"pk": self.customer.pk, "cart_item_pk": cart_item.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
