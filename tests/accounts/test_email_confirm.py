from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator


class EmailConfirmationTests(APITestCase):

    
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email="test@test.com", password="123")
        self.token = default_token_generator.make_token(user=self.user)
        self.url = reverse("accounts:confirm_email", kwargs={'pk':self.user.pk})

    def test_success_email_confirm(self):
        
        data = {
            'token': self.token,
        }

        self.assertFalse(self.user.email_confirmed)

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        
        self.assertTrue(self.user.email_confirmed)

    def test_invalid_user_pk_failure(self):
        
        data = {
            'token': self.token,
        }

        url = reverse("accounts:confirm_email", kwargs={'pk':self.user.pk+1})
        self.assertFalse(self.user.email_confirmed)

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        
        self.assertFalse(self.user.email_confirmed)
        

    def test_invalid_token_failure(self):
        data = {
            'token': self.token + "bla",
        }

        self.assertFalse(self.user.email_confirmed)

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        
        self.assertFalse(self.user.email_confirmed)

    def test_previously_confirmed_email(self):
        data = {
            'token': self.token,
        }

        self.assertFalse(self.user.email_confirmed)

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        
        self.assertTrue(self.user.email_confirmed)

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.user.refresh_from_db()
        
        self.assertTrue(self.user.email_confirmed)




