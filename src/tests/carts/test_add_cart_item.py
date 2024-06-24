from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.store_factories import StoreFactory
from tests.factories.products_factories import (
    ProductFactory,
    AlbumItemFactory,
    InventoryFactory,
)
from tests.factories.carts_factories import CartItemFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    generate_auth_token,
    create_groups,
    create_reviewer
)


class CartItemCreateTests(APITestCase):
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
        cls.customer = create_customer(email="customer@test.com")
        cls.token = generate_auth_token(cls.customer.user)
        cls.url = reverse("customers:cart_items", kwargs={'pk': cls.customer.pk})
        cls.valid_data = {'product_ids': [cls.product.pk]}
        
    
    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        distributor_token = generate_auth_token(self.distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        url = reverse("customers:cart_items", kwargs={'pk': self.distributor.pk})
        response = self.client.post(url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer(email="reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        url = reverse("customers:cart_items", kwargs={'pk': reviewer.pk})
        response = self.client.post(url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_not_same_customer_failure(self):
        url = reverse("customers:cart_items", kwargs={'pk': self.customer.pk+1})
        response = self.client.post(url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_product_not_exist_failure(self):
        data = {'product_ids': [self.product.pk+1]}
        
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_cart_item_failure(self):
        CartItemFactory.create(product=self.product, customer=self.customer)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
    
    def test_cart_item_add_success(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_bulk_add_cart_items(self):
        product = ProductFactory.create()
        InventoryFactory.create(store=self.store, product=product)
        AlbumItemFactory.create(product=product, is_cover=True)
        data = {'product_ids': [product.pk, self.product.pk]}

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    # def test_quantity()
