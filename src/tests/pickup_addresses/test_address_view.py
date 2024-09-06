from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.addresses_factories import PickupAddressFactory, CityFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_all_users_except,
    generate_auth_token,
    create_groups,
)


class PickupAddressRetrieveTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.customer = create_customer("customer@test.com")
        cls.address = PickupAddressFactory.create(customer=cls.customer)
        cls.url = reverse(
            "customers:address",
            kwargs={"pk": cls.customer.pk, "address_pk": cls.address.pk},
        )

    def test_unauthenticated_failure(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_customer_failure(self):
        distributor = create_distributor("distributor@test.com")
        distributor_token = generate_auth_token(distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        url = reverse(
            "customers:address",
            kwargs={"pk": distributor.pk, "address_pk": self.address.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        url = reverse(
            "customers:address",
            kwargs={"pk": reviewer.pk, "address_pk": self.address.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_success(self):
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_same_customer_failure(self):
        customer = create_customer("customer2@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_address_not_exist_failure(self):
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        customer2 = create_customer("customer2@test.com")
        address = PickupAddressFactory.create(
            customer=customer2
        )
        url = reverse(
            "customers:address",
            kwargs={"pk": self.customer.pk, "address_pk": address.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PickupAddressUpdateTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.customer = create_customer("customer@test.com")
        cls.address = PickupAddressFactory.create(
            customer=cls.customer
        )
        cls.city = cls.address.city
        cls.city2 = CityFactory.create(name="city2")
        cls.url = reverse(
            "customers:address",
            kwargs={"pk": cls.customer.pk, "address_pk": cls.address.pk},
        )
        cls.data = {
            'city_id' : cls.city2.pk,
            'address': "Street 2 house 3",
        }
    
    def setUp(self) -> None:
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_customer_failure(self):
        distributor = create_distributor("distributor@test.com")
        distributor_token = generate_auth_token(distributor.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {distributor_token}")
        url = reverse(
            "customers:address",
            kwargs={"pk": distributor.pk, "address_pk": self.address.pk},
        )
        response = self.client.patch(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer("reviewer@test.com")
        reviewer_token = generate_auth_token(reviewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reviewer_token}")
        url = reverse(
            "customers:address",
            kwargs={"pk": reviewer.pk, "address_pk": self.address.pk},
        )
        response = self.client.patch(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_address_update_success(self):
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_not_same_customer_failure(self):
        customer = create_customer("customer2@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_address_not_exist_failure(self):
        customer2 = create_customer("customer2@test.com")
        address = PickupAddressFactory.create(customer=customer2)
        url = reverse(
            "customers:address",
            kwargs={"pk": self.customer.pk, "address_pk": address.pk},
        )
        response = self.client.patch(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_city_failure(self):
        data = {"city_id": 1231}
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PickupAddressDeleteTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.customer = create_customer("customer@test.com")
        cls.address = PickupAddressFactory.create(
            customer=cls.customer
        )
        cls.url = reverse(
            "customers:address",
            kwargs={"pk": cls.customer.pk, "address_pk": cls.address.pk},
        )
        
    
    def setUp(self) -> None:
        customer_token = generate_auth_token(self.customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")

    def test_unauthenticated_failure(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_customer_failure(self):
        users = generate_all_users_except("Customer")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
            url = reverse(
                "customers:address",
                kwargs={"pk": user.pk, "address_pk": self.address.pk},
            )
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_address_delete_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_not_same_customer_failure(self):
        customer = create_customer("customer2@test.com")
        customer_token = generate_auth_token(customer.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {customer_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_address_not_exist_failure(self):
        customer2 = create_customer("customer2@test.com")
        address = PickupAddressFactory.create(customer=customer2)
        url = reverse(
            "customers:address",
            kwargs={"pk": self.customer.pk, "address_pk": address.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
