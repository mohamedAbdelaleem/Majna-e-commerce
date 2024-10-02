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


class ReviewListTests(APITestCase):
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
        cls.url = reverse("products:reviews", kwargs={"pk": cls.product.pk})

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


    def test_unauthenticated_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_role_independent(self):
        users = generate_all_users_except("Reviewer")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_not_found_failure(self):
        url = reverse("products:reviews", kwargs={"pk": 3123})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_list_count(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data["results"]), 1)
