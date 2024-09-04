import json
from django.urls import reverse
from django.db.models import Sum
from rest_framework.test import APITestCase
from rest_framework import status
from orders.models import Order
from products.models import Inventory
from tests.factories.products_factories import ProductFactory, InventoryFactory
from tests.factories.store_factories import StoreFactory
from tests.factories.addresses_factories import PickupAddressFactory
from tests.factories.auth_factories import (
    create_distributor,
    generate_auth_token,
    create_groups,
    create_customer,
    create_reviewer,
)


class OrderCreateTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)

        cls.product = ProductFactory.create(name="name", description="description")
        cls.inventory = InventoryFactory.create(
            store=cls.store, product=cls.product, quantity=10
        )
        cls.product2 = ProductFactory.create(name="name", description="description")
        cls.inventory2 = InventoryFactory.create(
            store=cls.store, product=cls.product2, quantity=10
        )

        cls.customer = create_customer("customer@gmail.com")
        cls.pickup_address = PickupAddressFactory.create(customer=cls.customer)

        cls.url = reverse("orders:orders")
        cls.valid_data = {
            "order_items": [{"product_id": cls.product.pk, "quantity": 2}],
            "pickup_address_id": cls.pickup_address.pk,
        }
        cls.json_data = json.dumps(cls.valid_data)

    def setUp(self) -> None:
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.post(
            self.url, self.valid_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(
            self.url, self.valid_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(
            self.url, self.valid_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_product_id(self):
        invalid_data_product_id = {
            "order_items": [{"product_id": 9999, "quantity": 2}],
            "pickup_address_id": self.pickup_address.pk,
        }
        json_data = json.dumps(invalid_data_product_id)
        response = self.client.post(
            self.url,
            json_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_values_failure(self):
        invalid_data_negative_quantity = {
            "order_items": [{"product_id": self.product.pk, "quantity": -1}],
            "pickup_address_id": self.pickup_address.pk,
        }
        json_data = json.dumps(invalid_data_negative_quantity)
        response = self.client.post(
            self.url,
            json_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_enough_inventory_failure(self):
        invalid_data_not_enough_inventory = {
            "order_items": [{"product_id": self.product.pk, "quantity": 20}],
            "pickup_address_id": self.pickup_address.pk,
        }
        json_data = json.dumps(invalid_data_not_enough_inventory)
        response = self.client.post(
            self.url,
            json_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_pickup_address(self):
        data = {
            "order_items": [{"product_id": self.product.pk, "quantity": 2}],
            "pickup_address_id": self.pickup_address.pk + 3,
        }
        json_data = json.dumps(data)
        response = self.client.post(
            self.url,
            json_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        customer2 = create_customer("customer2@gmail.com")
        pickup_address = PickupAddressFactory.create(customer=customer2)
        data = {
            "order_items": [{"product_id": self.product.pk, "quantity": 2}],
            "pickup_address_id": pickup_address.pk,
        }
        json_data = json.dumps(data)
        response = self.client.post(
            self.url,
            json_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_place_order(self):
        orders_count_before = Order.objects.filter(customer_id=self.customer.pk).count()
        response = self.client.post(
            self.url, self.json_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        orders_count_after = Order.objects.filter(customer_id=self.customer.pk).count()
        self.assertEqual(orders_count_after, orders_count_before + 1)

    def test_place_multiple_products(self):
        data = {
            "order_items": [
                {"product_id": self.product.pk, "quantity": 3},
                {"product_id": self.product2.pk, "quantity": 3},
            ],
            "pickup_address_id": self.pickup_address.pk,
        }
        orders_count_before = Order.objects.filter(customer_id=self.customer.pk).count()
        json_data = json.dumps(data)
        response = self.client.post(
            self.url, json_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        orders_count_after = Order.objects.filter(customer_id=self.customer.pk).count()
        self.assertEqual(orders_count_after, orders_count_before + 1)

    def test_max_products_failure(self):
        data = {
            "order_items": [
                {"product_id": self.product.pk, "quantity": 3},
                {"product_id": self.product2.pk, "quantity": 3},
                {"product_id": ProductFactory.create().pk, "quantity": 3},
                {"product_id": ProductFactory.create().pk, "quantity": 3},
                {"product_id": ProductFactory.create().pk, "quantity": 3},
                {"product_id": ProductFactory.create().pk, "quantity": 3},
            ],
            "pickup_address_id": self.pickup_address.pk,
        }
        orders_count_before = Order.objects.filter(customer_id=self.customer.pk).count()
        json_data = json.dumps(data)
        response = self.client.post(
            self.url, json_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        orders_count_after = Order.objects.filter(customer_id=self.customer.pk).count()
        self.assertEqual(orders_count_after, orders_count_before)

    def test_inventory_after_order_placement(self):
        data = {
            "order_items": [{"product_id": self.product.pk, "quantity": 2}],
            "pickup_address_id": self.pickup_address.pk,
        }
        quantity_before = Inventory.objects.filter(
            product_id=self.product.pk
        ).aggregate(total=Sum("quantity"))["total"]
        json_data = json.dumps(data)
        response = self.client.post(
            self.url, json_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        quantity_after = Inventory.objects.filter(
            product_id=self.product.pk
        ).aggregate(total=Sum("quantity"))["total"]

        self.assertEqual(quantity_after + 2, quantity_before)
