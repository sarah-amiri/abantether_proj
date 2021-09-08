from pymongo import MongoClient

from django.conf import settings
from django.test import TestCase

from apps.account.serializers import AccountTypeSerializer
from apps.account.tests.factories import AccountTypeFactory

# Todo: Add test database for mongodb


class AccountTypeSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account_type = None
        cls.client = MongoClient(settings.MONGO_HOST)
        cls.db = cls.client[settings.MONGO_DB]

    def test_account_type_is_created_correctly(self):
        data = {
            'code': 'ATIRR',
            'name': 'AccountTypeIRR',
            'currency': 'IRR'
        }
        serializer = AccountTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        serializer.is_valid()
        self.account_type = serializer.save()

        collection = self.db['account_type']
        result = list(
            collection.find({'code': 'ATIRR'})
        )
        self.assertEqual(len(result), 2)

    def test_account_type_not_created_with_incomplete_parameters(self):
        data = {
            'code': 'ATIRR',
            'currency': 'IRR'
        }
        serializer = AccountTypeSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_account_type_not_created_with_duplicate_code(self):
        data = {
            'code': 'ATIRR',
            'name': 'AccountTypeTRY',
            'currency': 'TRY'
        }
        serializer = AccountTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
