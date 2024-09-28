from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import AlbumItem
from products.services import MAX_ALBUM_ITEMS
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


class AddAlbumItemTests(APITestCase):
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
        cls.url = reverse("products:album_items", kwargs={"pk": cls.product.pk})
        cls.valid_file = SimpleUploadedFile(
            name="album_item.png",
            content=b"A" * settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
            content_type="image/png",
        )
        cls.invalid_file_size = SimpleUploadedFile(
            name="name.jpg",
            content=b"A" * (settings.FILE_UPLOAD_MAX_MEMORY_SIZE + 1),
            content_type="image/*",
        )
        cls.invalid_file_format = SimpleUploadedFile(
            name="name.pdf",
            content=b"A" * (settings.FILE_UPLOAD_MAX_MEMORY_SIZE - 1),
            content_type="application/pdf",
        )
        cls.valid_data = {"image": cls.valid_file, "is_cover": False}

    def setUp(self) -> None:
        self.token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        users = generate_all_users_except("Distributor")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

            response = self.client.post(self.url, self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_distributor_failure(self):
        distributor = create_distributor("distributor2@test.com")
        token = generate_auth_token(distributor.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_not_found_failure(self):
        url = reverse("products:album_items", kwargs={"pk": 3123})
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_file_format_failure(self):
        data = self.valid_data.copy()
        data["image"] = self.invalid_file_format
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_file_size_failure(self):
        data = self.valid_data.copy()
        data["image"] = self.invalid_file_size
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_album_item_creation(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_success_cover_item_creation(self):
        data = self.valid_data.copy()
        data["is_cover"] = True
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        cover_items_count = AlbumItem.objects.filter(
            product_id=self.product.pk, is_cover=True
        ).count()
        self.assertEqual(cover_items_count, 1)

    def test_max_album_items_number(self):
        for i in range(MAX_ALBUM_ITEMS-1):
            AlbumItemFactory.create(product=self.product, is_cover=False)
        
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
