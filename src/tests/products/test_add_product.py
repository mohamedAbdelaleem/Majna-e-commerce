from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.brand_related_factories import BrandFactory, BrandDistributorsFactory
from tests.factories.store_factories import StoreFactory
from tests.factories.products_factories import SubCategoryFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_auth_token,
    create_groups
)


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
        cls.token = generate_auth_token(cls.distributor)

        cls.valid_file = SimpleUploadedFile(
            name="name.jpg",
            content=b"A" * settings.FILE_UPLOAD_MAX_MEMORY_SIZE - 1,
            content_type="image/*",
        )

        cls.invalid_file_size = SimpleUploadedFile(
            name="name.jpg",
            content=b"A" * settings.FILE_UPLOAD_MAX_MEMORY_SIZE + 1,
            content_type="image/*",
        )
        cls.invalid_file_formate = SimpleUploadedFile(
            name="name.pdf",
            content=b"A" * settings.FILE_UPLOAD_MAX_MEMORY_SIZE - 1,
            content_type="application/pdf",
        )
        cls.data = {
            "title": "title",
            "description": "description",
            "price": 12.3,
            "subcategory": cls.sub_category.pk,
            "stores": [
                {"store_id": cls.store1.pk, "quantity":3},
                {"store_id": cls.store2.pk, "quantity":3},

            ],
            "brand": cls.brand.id,
            "album": [
                {"image": cls.valid_file, "is_cover": False},
                {"image": cls.valid_file, "is_cover": True},
            ]
        }

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_unauthenticated_user_failure(self):
        self.client.credentials()
        response = self.client.post(self.url, data={})
        self.assertEqual(response, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_failure(self):
        customer = create_customer(email="customer@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.post(self.url, data={})
        self.assertEqual(response, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer(email="reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        response = self.client.post(self.url, data={})
        self.assertEqual(response, status.HTTP_403_FORBIDDEN)
    
    def test_unauthorized_distributor(self):
        unauthorized_distributor = create_distributor(email="distributor@gmail.com")
        store3 = StoreFactory.create(distributor=unauthorized_distributor)
        token = generate_auth_token(self.unauthorized_distributor)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        data = self.data
        data["stores"] = [{"store_id": store3.pk, "quantity":3}]
        response = self.client.post(self.url, data=data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)   #  unauthorized_distributor is not yet authorized for the brand

    def test_max_album_items_failure(self):
        album_items = [{"image": self.valid_file, "is_cover": False} for i in range(9)]
        data = self.data
        data['album'].extend(album_items)
        response = self.client.post(self.url, data=data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_image_size(self):
        data = self.data
        data["album"] = [{"image": self.invalid_file_size, "is_cover":True}]
        response = self.client.post(self.url, data=data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_image_file_format(self):
        data = self.data
        data["album"] = [{"image": self.invalid_file_formate, "is_cover":True}]
        response = self.client.post(self.url, data=data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
    
    def test_missing_cover_image_failure(self):
        data = self.data
        data["album"] = [{"image": self.valid_file, "is_cover":False}]
        response = self.client.post(self.url, data=data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_album_failure(self):
        data = self.data
        data["album"] = []
        response = self.client.post(self.url, data=data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_values_failure(self):
        data = self.data
        data['price'] = -1
        response = self.client.post(self.url, data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["price"] = 12
        data["stores"][0]["quantity"] = -1
        response = self.client.post(self.url, data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        