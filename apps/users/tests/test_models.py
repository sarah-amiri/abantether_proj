from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class CreateUserTestCase(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_superuser(username='admin', password='12341234')
        self.client = User.objects.create_user(username='client', password='12341234')
        self.supporter = User.objects.create_user(username='supporter', password='12341234', is_supporter=True)

    def test_admin_does_not_create_other_models(self):
        self.assertFalse(hasattr(self.admin, 'profile'))
        self.assertFalse(hasattr(self.admin, 'supportmember'))

    def test_client_creates_profile_model(self):
        self.assertTrue(hasattr(self.client, 'profile'))
        self.assertFalse(hasattr(self.client, 'supportmember'))

    def test_supporter_creates_supporter_member_model(self):
        self.assertFalse(hasattr(self.supporter, 'profile'))
        self.assertTrue(hasattr(self.supporter, 'supportmember'))
