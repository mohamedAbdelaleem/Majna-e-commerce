from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.addresses_factories import PickupAddressFactory
from tests.factories.orders_factories import create_test_order
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


class CustomerOrderListTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product1 = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product1, quantity=15)
        cls.cover_image = AlbumItemFactory.create(product=cls.product1, is_cover=True)
        cls.customer = create_customer("customer@test.com")
        cls.pickup_address = PickupAddressFactory.create(customer=cls.customer)
        cls.order = create_test_order(cls.customer, cls.pickup_address, cls.product1, 5, cls.store)

        cls.customer2 = create_customer("customer2@test.com")
        cls.pickup_address2 = PickupAddressFactory.create(customer=cls.customer)
        cls.order = create_test_order(cls.customer2, cls.pickup_address2, cls.product1, 5, cls.store)

        cls.url = reverse("customers:orders", kwargs={'pk': cls.customer.pk})

    def test_unauthenticated_failure(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_customer_failure(self):
        distributor_token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        url = reverse("customers:orders", kwargs={'pk': self.distributor.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        url = reverse("customers:orders", kwargs={'pk': reviewer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_success(self):
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_not_same_customer_failure(self):
        customer_token = generate_auth_token(self.customer2.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieved_orders_count(self):
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 1)


# delivery