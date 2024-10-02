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


class DeleteReviewTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.customer = create_customer("customer@test.com")
        cls.pickup_address = PickupAddressFactory.create(customer=cls.customer)
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product)
        cls.cover_image = AlbumItemFactory.create(product=cls.product, is_cover=True)
        order = create_test_order(
            cls.customer,
            cls.pickup_address,
            cls.product,
            3,
            cls.store,
            "delivered"
        )
        cls.review1 = ReviewFactory.create(customer=cls.customer, product=cls.product, order_date=order.ordered_at)
        cls.url = reverse("products:review", kwargs={"pk": cls.product.pk, "review_pk": cls.review1.pk})

        cls.product2 = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product2)
        cls.cover_image = AlbumItemFactory.create(product=cls.product2, is_cover=True)
        order = create_test_order(
            cls.customer,
            cls.pickup_address,
            cls.product2,
            3,
            cls.store,
            "delivered"
        )
        cls.review2 = ReviewFactory.create(customer=cls.customer, product=cls.product2, order_date=order.ordered_at)

    def setUp(self) -> None:
        self.token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        users = generate_all_users_except("Customer")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_not_found_failure(self):
        url = reverse("products:review", kwargs={"pk": 3123, "review_pk": self.review1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_not_found_failure(self):
        url = reverse("products:review", kwargs={"pk": self.product.pk, "review_pk": self.review2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_success_review_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
