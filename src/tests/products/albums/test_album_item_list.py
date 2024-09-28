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
    create_distributor,
    generate_all_users_except,
    generate_auth_token,
    create_groups,
)


class AlbumItemListTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product)
        cls.cover_image = AlbumItemFactory.create(product=cls.product, is_cover=True)
        AlbumItemFactory.create(product=cls.product)
        cls.url = reverse("products:album_items", kwargs={"pk": cls.product.pk})
        cls.product2 = ProductFactory.create(
            name="Samsung new phone", description="New phone From Samsung"
        )
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product2)
        cls.cover_image = AlbumItemFactory.create(product=cls.product2, is_cover=True)


    def setUp(self) -> None:
        self.token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        users = generate_all_users_except("Distributor")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_distributor_failure(self):
        distributor = create_distributor("distributor2@test.com")
        token = generate_auth_token(distributor.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_not_found_failure(self):
        url = reverse("products:album_items", kwargs={"pk": 3123})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_success_album_item_list_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["album_items"]), 2)
