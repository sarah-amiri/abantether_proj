from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserCreateTestCase(TestCase):
    def setUp(self) -> None:
        self.url = reverse('register')
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.client = Client()

    def test_user_can_register_correctly(self):
        data = {
            'username': 'test_user',
            'password': '12341234',
            'email': 'test_user@mail.com',
            'first_name': 'test first name',
            'last_name': 'test last name'
        }
        response = self.client.post(self.url, data, content_type='application/json')
        user = User.objects.get(username='test_user')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(user.email, 'test_user@mail.com')
        self.assertTrue(hasattr(user, 'profile'))

    def test_support_member_can_register_correctly(self):
        pass

    def test_admin_can_register_correctly(self):
        pass

    def test_user_can_not_register_without_username(self):
        data = {
            'email': 'test_user@mail.com',
            'password': '12341234',
            'profile': {
                'mobile': '123456789'
            }
        }
        response = self.client.post(self.url, data, content_type='application/json')
        x = response.raise_for_status()
        self.assertEqual(response.status_code, 404)

    def test_support_member_can_not_register_with_duplicate_username(self):
        pass

    def test_admin_can_not_register_without_password(self):
        pass


class UserLoginTestCase(TestCase):
    def setUp(self) -> None:
        pass

    def test_user_can_login_successfully(self):
        pass

    def test_user_can_not_login_without_username_or_password(self):
        pass

    def test_user_can_not_login_without_correct_username_and_password(self):
        pass
