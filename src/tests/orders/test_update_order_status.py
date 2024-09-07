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
    create_delivery,
    create_distributor,
    generate_all_users_except,
    generate_auth_token,
    create_groups,
)


class OrderDetailsTests(APITestCase):
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
        
        cls.delivery = create_delivery("delivery@test.com")
        cls.url = reverse("orders:order", kwargs={'pk': cls.order.pk})

    def test_unauthenticated_failure(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_customer_failure(self):
        users = generate_all_users_except("Delivery")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
            url = reverse("orders:orders")
            response = self.client.patch(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delivery_success_shipped_update(self):
        data = {"status": "Shipped"}
        delivery_token = generate_auth_token(self.delivery)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {delivery_token}")
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delivery_success_delivered_update(self):
        self.order.status = "shipped"
        self.order.save()
        data = {"status": "delivered"}
        delivery_token = generate_auth_token(self.delivery)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {delivery_token}")
        response = self.client.patch(self.url, data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_reverse_update(self):
        self.order.status = "shipped"
        self.order.save()
        data = {"status": "Placed"}
        delivery_token = generate_auth_token(self.delivery)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {delivery_token}")
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        self.order.status = "delivered"
        self.order.save()
        data = {"status": "Placed"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        response = self.client.patch(self.url, {"status": "Shipped"})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_invalid_status(self):
        data = {"status": "bla"}
        delivery_token = generate_auth_token(self.delivery)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {delivery_token}")
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
