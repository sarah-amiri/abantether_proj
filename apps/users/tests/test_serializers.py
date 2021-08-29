from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.users.models import Profile, SupportMember
from apps.users.serializers import UserSerializer

User = get_user_model()


class UserSerializerTestCase(TestCase):
    def setUp(self) -> None:
        client_data = {
            'username': 'test',
            'password': '12341234',
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'email': 'test@mail.com'
        }
        self.client = User.objects.create_user(**client_data)
        Profile.objects.create(user=self.client)

        supporter_data = {
            'username': 'supporter1',
            'password': '12341234',
            'first_name': 'support_first_name',
            'last_name': 'support_last_name',
            'email': 'support@mail.com',
            'is_supporter': True
        }
        self.support_member = User.objects.create_user(**supporter_data)
        SupportMember.objects.create(user=self.support_member)

        admin_data = {
            'username': 'admin_test',
            'password': '12341234',
            'email': 'admin@mail.com',
            'is_staff': True
        }
        self.admin = User.objects.create_user(**admin_data)

    def test_serializer_gets_client_data_correctly(self):
        serializer = UserSerializer(self.client)
        data = serializer.data
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data['username'], 'test')
        self.assertEqual(data['first_name'], 'test_first_name')
        self.assertEqual(data['last_name'], 'test_last_name')
        self.assertEqual(data['email'], 'test@mail.com')
        self.assertFalse(data['is_staff'])
        self.assertFalse(data['is_supporter'])
        self.assertIsNone(data.get('password'))
        self.assertIsNotNone(data.get('profile'))
        self.assertFalse(data['profile']['is_mobile_verified'])

    def test_serializer_gets_support_member_data_correctly(self):
        serializer = UserSerializer(self.support_member)
        data = serializer.data
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data['username'], 'supporter1')
        self.assertEqual(data['first_name'], 'support_first_name')
        self.assertEqual(data['last_name'], 'support_last_name')
        self.assertEqual(data['email'], 'support@mail.com')
        self.assertFalse(data['is_staff'])
        self.assertTrue(data['is_supporter'])
        self.assertIsNone(data.get('password'))
        self.assertIsNotNone(data.get('supportmember'))
        self.assertIsNotNone(data['supportmember'].get('id'))

    def test_serializer_gets_admin_data_correctly(self):
        serializer = UserSerializer(self.admin)
        data = serializer.data
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data['username'], 'admin_test')
        self.assertEqual(data['email'], 'admin@mail.com')
        self.assertTrue(data['is_staff'])
        self.assertFalse(data['is_supporter'])
        self.assertFalse(data['is_superuser'])
        self.assertIsNone(data.get('password'))

    def test_serializer_receives_client_data_correctly(self):
        create_client_data = {
            'username': 'test_user',
            'email': 'test_user@mail.com',
            'password': '12341234',
            'profile': {
                'mobile': '123456789',
                'is_mobile_verified': True
            }
        }
        ser = UserSerializer(data=create_client_data)
        ser.is_valid()
        created_client = ser.save()

        self.assertTrue(hasattr(created_client, 'id'))
        self.assertEqual(created_client.username, 'test_user')
        self.assertTrue(hasattr(created_client, 'password'))
        self.assertTrue(hasattr(created_client, 'profile'))
        self.assertTrue(created_client.profile.is_mobile_verified)

    def test_serializer_receives_support_member_data_correctly(self):
        create_support_member_data = {
            'username': 'test_user',
            'email': 'test_user@mail.com',
            'password': '12341234',
            'is_supporter': True,
            'supportmember': {}
        }
        ser = UserSerializer(data=create_support_member_data)
        ser.is_valid()
        created_support_member = ser.save()

        self.assertTrue(hasattr(created_support_member, 'id'))
        self.assertEqual(created_support_member.username, 'test_user')
        self.assertTrue(hasattr(created_support_member, 'password'))
        self.assertTrue(hasattr(created_support_member, 'supportmember'))
        self.assertTrue(created_support_member.is_supporter)

    def test_serializer_receives_admin_data_correctly(self):
        create_admin_data = {
            'username': 'test_user_admin',
            'email': 'test_user_admin@mail.com',
            'password': '12341234',
            'is_staff': True
        }
        ser = UserSerializer(data=create_admin_data)
        ser.is_valid()
        created_admin = ser.save()

        self.assertTrue(hasattr(created_admin, 'id'))
        self.assertEqual(created_admin.username, 'test_user_admin')
        self.assertTrue(hasattr(created_admin, 'password'))
        self.assertFalse(hasattr(created_admin, 'profile'))
        self.assertFalse(hasattr(created_admin, 'supportmember'))
        self.assertTrue(created_admin, 'is_staff')
        self.assertTrue(created_admin, 'is_superuser')
