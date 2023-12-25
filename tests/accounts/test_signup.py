from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.test import APITestCase
from rest_framework import status


class SignUpTests(APITestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")
        user = get_user_model().objects.create_user(
            email="test@test.com", username="test", password="12345aa"
        )
        self.user = user

    def test_success_signup(self):
        data = {
            "email": "test1@test.com",
            "username": "testuser",
            "password": "12345aa",
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:
            user = get_user_model().objects.get(email=data["email"])
            # check encryption
            self.assertNotEqual(user.password, data["password"])
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist: the user wasn't created")

    def test_missing_credential_failure(self):
        missing_email = {
            "username": "testuser",
            "password": "12345aa",
        }

        missing_username = {
            "email": "test1@test.com",
            "password": "12345aa",
        }

        missing_password = {
            "email": "test1@test.com",
            "username": "testuser",
        }

        missing_email_response = self.client.post(self.url, missing_email)
        self.assertEqual(
            missing_email_response.status_code, status.HTTP_400_BAD_REQUEST
        )

        missing_username_response = self.client.post(self.url, missing_username)
        self.assertEqual(
            missing_username_response.status_code, status.HTTP_400_BAD_REQUEST
        )

        missing_password_response = self.client.post(self.url, missing_password)
        self.assertEqual(
            missing_password_response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_existing_email_failure(self):
        data = {"email": self.user.email, "username": "test", "password": "12345aa"}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_insensitive_email_failure(self):
        data = {"email": "Test@test.com", "username": "test", "password": "12345aa"}

        email_with_dots_data = {
            "email": "te.st@test.com",
            "username": "test",
            "password": "12345aa",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, email_with_dots_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_failure(self):
        data = {
            "email": "test1@test.com",
            "username": "testuser",
            "password": "123",
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_unconfirmed_after_success(self):
        pass
