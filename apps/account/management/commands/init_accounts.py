from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from apps.account.models import Account, AccountType
from apps.account.names import (
    initial_account_name,
    unpaid_account_type_name,
    unpaid_account_type_code
)

CURRENCIES = [i for i in settings.CURRENCIES]


class Command(BaseCommand):

    @staticmethod
    def get_currency_account(currency):
        name = initial_account_name.format(currency)
        return Account.objects(name=name).first()

    @staticmethod
    def get_currency_account_type(currency):
        code = unpaid_account_type_code.format(currency)
        return AccountType.objects(code=code).first()

    @staticmethod
    def create_currency_account(currency, account_type):
        account = Account(
            name=initial_account_name.format(currency),
            user_id=0,
            user_username='unpaid',
            account_type=account_type,
            currency=currency,
            balance_limit=-1,
            created_time=timezone.now(),
            modified_time=timezone.now()
        )
        account.save()

    @staticmethod
    def create_currency_account_type(currency):
        account_type = AccountType(
            code=unpaid_account_type_code.format(currency),
            name=unpaid_account_type_name,
            currency=currency,
            created_time=timezone.now()
        )
        return account_type.save()

    def handle(self, *args, **options):
        for currency in CURRENCIES:
            account = self.get_currency_account(currency)
            if not account:
                account_type = self.get_currency_account_type(currency)
                if not account_type:
                    account_type = self.create_currency_account_type(currency)
                self.create_currency_account(currency, account_type)

            print(f'Account is now available for currency {currency}')
