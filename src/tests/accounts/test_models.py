from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Distributor, Customer

class DistributorModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_user(email='test@test.com', password="123")
        cls.user2 = get_user_model().objects.create_user(email='test2@test.com', password="123")

    def test_id_generation_on_save(self):
        distributor = Distributor(user=self.user2)
        distributor.save()

        expected_id = self.user2.id
        users_count = get_user_model().objects.count()
        distributors_count = Distributor.objects.count()

        self.assertGreater(users_count, distributors_count)
        self.assertEqual(distributor.id, expected_id)

    def test_id_not_overwritten_on_save(self):
        custom_id = 7
        distributor = Distributor(user=self.user2, id=custom_id)
        distributor.save()

        self.assertNotEqual(distributor.id, custom_id)


class CustomerModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_user(email='test@test.com', password="123")
        cls.user2 = get_user_model().objects.create_user(email='test2@test.com', password="123")

    def test_id_generation_on_save(self):
        customer = Customer(user=self.user2)
        customer.save()

        expected_id = self.user2.id
        users_count = get_user_model().objects.count()
        customers_count = Customer.objects.count()

        self.assertGreater(users_count, customers_count)
        self.assertEqual(customer.id, expected_id)

    def test_id_not_overwritten_on_save(self):
        custom_id = 7
        customer = Customer(user=self.user, id=custom_id)
        customer.save()

        self.assertNotEqual(customer.id, custom_id)
