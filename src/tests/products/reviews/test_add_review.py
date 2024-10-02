from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.addresses_factories import PickupAddressFactory
from tests.factories.orders_factories import create_test_order
from tests.factories.reviews_factories import ReviewFactory
from tests.factories.store_factories import StoreFactory
from tests.factories.products_factories import (
    ProductFactory,
    AlbumItemFactory,
    InventoryFactory,
)
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    generate_all_users_except,
    generate_auth_token,
    create_groups,
)


class AddReviewTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        InventoryFactory.create(store=cls.store, product=cls.product)
        AlbumItemFactory.create(product=cls.product, is_cover=True)
        cls.product2 = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        InventoryFactory.create(store=cls.store, product=cls.product2)
        AlbumItemFactory.create(product=cls.product2, is_cover=True)
        cls.url = reverse("products:reviews", kwargs={"pk": cls.product.pk})
        
        cls.customer = create_customer("customer@test.com")
        cls.pickup_address = PickupAddressFactory.create(customer=cls.customer)
        cls.valid_data = {
            "rating": 5,
            "content": "Good Product"
        }

    def setUp(self) -> None:
        self.token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        users = generate_all_users_except("Customer")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

            response = self.client.post(self.url, self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_not_found_failure(self):
        url = reverse("products:reviews", kwargs={"pk": 3123})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_not_ordered_failure(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_not_delivered_failure(self):
        create_test_order(
            self.customer,
            self.pickup_address,
            self.product,
            5,
            self.store
        )
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_review_data_failure(self):
        data = {
            "rating": 6
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "rating": -1
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_review_creation(self):
        create_test_order(
            self.customer,
            self.pickup_address,
            self.product,
            5,
            self.store,
            "delivered"
        )
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_already_reviewed_failure(self):
        order = create_test_order(
            self.customer,
            self.pickup_address,
            self.product,
            5,
            self.store,
            "delivered"
        )
        ReviewFactory.create(customer=self.customer, product=self.product, order_date=order.ordered_at)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)