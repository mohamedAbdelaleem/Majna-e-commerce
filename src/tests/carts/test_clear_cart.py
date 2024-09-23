from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from carts.models import CartItem
from tests.factories import auth_factories
from tests.factories.carts_factories import CartItemFactory
from tests.factories.products_factories import AlbumItemFactory, InventoryFactory, ProductFactory
from tests.factories.store_factories import StoreFactory


class ClearCartTests(APITestCase):
    
    @classmethod
    def setUpTestData(cls) -> None:
        auth_factories.create_groups()
        cls.customer = auth_factories.create_customer("customer@test.com")
        cls.distributor = auth_factories.create_distributor("distributor@test.com")
        cls.store = StoreFactory.create(distributor=cls.distributor)
        cls.product1 = ProductFactory.create()
        cls.inventory = InventoryFactory.create(store=cls.store, product=cls.product1)
        cls.cover_image = AlbumItemFactory.create(product=cls.product1, is_cover=True)
        cls.cart_item = CartItemFactory.create(
            customer=cls.customer, product=cls.product1
        )
        cls.customer2 = auth_factories.create_customer("customer2@test.com")
        cls.cart_item2 = CartItemFactory.create(
            customer=cls.customer2, product=cls.product1
        )
        cls.url = reverse("customers:cart_items", kwargs={'pk': cls.customer.pk})


    def test_unauthenticated_failure(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_failure(self):
        users = auth_factories.generate_all_users_except("Customer")
        for role_user in users:
            if hasattr(role_user, "user"):
                token = auth_factories.generate_auth_token(role_user.user)
            else:
                token = auth_factories.generate_auth_token(role_user)
            
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



    def test_not_same_customer_failure(self):
        token = auth_factories.generate_auth_token(self.customer2.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        carts_count = CartItem.objects.count()
        self.assertEqual(carts_count, 2)


    def success_clear_cart(self):
        token = auth_factories.generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        carts_count = CartItem.objects.count()
        self.assertEqual(carts_count, 1)

