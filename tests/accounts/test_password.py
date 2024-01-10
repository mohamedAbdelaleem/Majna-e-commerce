from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from knox.models import AuthToken


class ChangePasswordTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_user(
            email="test@test.com", password="123"
        )
        cls.url = reverse("accounts:change_password", kwargs={'pk':cls.user.pk})
        instance, cls.token = AuthToken.objects.create(user=cls.user)

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_success_change_password(self):
        data = {
            "current_password": "123",
            "new_password": "123123aa",
            "re_new_password": "123123aa",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        check_new_password = self.user.check_password(data["new_password"])
        self.assertTrue(check_new_password)

        # check hashing
        self.assertFalse(self.user.password == data["new_password"])

    def test_wrong_current_password_failure(self):
        data = {
            "current_password": "1234",
            "new_password": "123123aa",
            "re_new_password": "123123aa",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        check_new_password = self.user.check_password(data["new_password"])
        self.assertFalse(check_new_password)

    def test_passwords_mismatch_failure(self):
        data = {
            "current_password": "123",
            "new_password": "123123aa",
            "re_new_password": "1212aa",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        check_new_password = self.user.check_password(data["new_password"])
        self.assertFalse(check_new_password)

    def test_invalid_password_failure(self):
        data = {
            "current_password": "123",
            "new_password": "123123",
            "re_new_password": "123123",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        check_new_password = self.user.check_password(data["new_password"])
        self.assertFalse(check_new_password)

    def test_unauthenticated_user(self):
        data = {
            "current_password": "123",
            "new_password": "123123aa",
            "re_new_password": "123123aa",
        }

        self.client.credentials()

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_not_same_user_failure(self):

        data = {
            "current_password": "123",
            "new_password": "123123aa",
            "re_new_password": "123123aa",
        }

        url = reverse("accounts:change_password", kwargs={'pk':self.user.pk+1})
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
