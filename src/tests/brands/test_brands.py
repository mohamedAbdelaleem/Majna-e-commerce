from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class BrandsTests(APITestCase):
    
    def test_retrieving_brands(self):

        url = reverse("brands:brands")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response.data, "brands")
