from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from products.services import MAX_ALBUM_ITEMS
from tests.factories.brand_related_factories import (
    BrandFactory,
    BrandDistributorsFactory,
)
from tests.factories.store_factories import StoreFactory
from tests.factories.products_factories import SubCategoryFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_auth_token,
    create_groups,
)


def generate_valid_image(name: str = "name.jpg"):
    valid_file = SimpleUploadedFile(
        name=name,
        content=b"A" * (settings.FILE_UPLOAD_MAX_MEMORY_SIZE - 1),
        content_type="image/*",
    )
    return valid_file


class AddProductTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("products:products")
        create_groups()

        cls.distributor = create_distributor(email="distributor@test.com")
        cls.brand = BrandFactory.create()
        BrandDistributorsFactory.create(distributor=cls.distributor, brand=cls.brand)
        cls.store1 = StoreFactory.create(distributor=cls.distributor)
        cls.store2 = StoreFactory.create(distributor=cls.distributor)

        cls.sub_category = SubCategoryFactory.create()
        cls.token = generate_auth_token(cls.distributor.user)

        cls.valid_file = generate_valid_image(name="name.jpg")
        cls.valid_file2 = generate_valid_image(name="name2.jpg")

        cls.invalid_file_size = SimpleUploadedFile(
            name="name.jpg",
            content=b"A" * (settings.FILE_UPLOAD_MAX_MEMORY_SIZE + 1),
            content_type="image/*",
        )
        cls.invalid_file_formate = SimpleUploadedFile(
            name="name.pdf",
            content=b"A" * (settings.FILE_UPLOAD_MAX_MEMORY_SIZE - 1),
            content_type="application/pdf",
        )
        cls.data = {
            "name": ["name"],
            "description": ["description"],
            "price": [12.3],
            "sub_category_pk": [cls.sub_category.pk],
            "inventory": [
                [
                    {"store_pk": cls.store1.pk, "quantity": 3},
                    {"store_pk": cls.store2.pk, "quantity": 3},
                ]
            ],
            "brand_pk": [cls.brand.id],
            "album": [
                [
                    {"image": "image-1", "is_cover": "False"},
                    {"image": "image-2", "is_cover": "True"},
                ]
            ],
            "image-1": [cls.valid_file],
            "image-2": [cls.valid_file2],
        }

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_unauthenticated_user_failure(self):
        self.client.credentials()
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_failure(self):
        customer = create_customer(email="customer@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer(email="reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_distributor(self):
        unauthorized_distributor = create_distributor(email="distributor@gmail.com")
        token = generate_auth_token(unauthorized_distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        data = self.data.copy()
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        print(response.content)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  #  unauthorized_distributor is not yet authorized for the brand

    def test_invalid_store(self):
        unauthorized_distributor = create_distributor(email="distributor@gmail.com")
        token = generate_auth_token(unauthorized_distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        BrandDistributorsFactory.create(
            distributor=unauthorized_distributor, brand=self.brand
        )
        response = self.client.post(
            self.url, data=self.data, media_type="multipart/form-data"
        )
        print(response.content)
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )  # should fail because the stores in cls.data["inventory"] don't belong to this distributor

    def test_max_album_items_failure(self):
        data = self.data.copy()
        album = []
        for i in range(1, MAX_ALBUM_ITEMS + 2):
            data[f"image-{i}"] = generate_valid_image(f"name_{i}.jpg")
            if i == 1:
                album.append({"image": f"image-{i}", "is_cover": "True"})
            else:
                album.append({"image": f"image-{i}", "is_cover": "False"})

        data["album"] = [album]
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_image_size(self):
        data = self.data.copy()
        data["album"] = [[{"image": "image-1", "is_cover": "True"}]]
        data["image-1"] = self.invalid_file_size
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_image_file_format(self):
        data = self.data.copy()
        data["album"] = [[{"image": "image-1", "is_cover": "True"}]]
        data["image-1"] = self.invalid_file_formate
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_cover_image_failure(self):
        data = self.data.copy()
        data["album"] = [[{"image": "image-1", "is_cover": "False"}]]
        data["image-1"] = self.valid_file
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_image_failure(self):
        data = self.data.copy()
        data["album"] = [[{"image": "image-1", "is_cover": "False"}]]
        del data["image-1"]
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_album_failure(self):
        data = self.data.copy()
        data["album"] = [[]]
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        del data["album"]
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_values_failure(self):
        data = self.data.copy()
        data["price"] = [-1]
        response = self.client.post(self.url, data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["price"] = [12]
        data["inventory"][0][0]["quantity"] = [-1]
        response = self.client.post(self.url, data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_product_create(self):
        response = self.client.post(
            self.url, self.data, media_type="multipart/form-data"
        )
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
