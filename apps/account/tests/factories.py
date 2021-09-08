import random
import string

from factory.django import DjangoModelFactory

from apps.account.models import AccountType

LETTERS = string.ascii_uppercase
LETTERS_NUMBERS = string.ascii_uppercase + string.ascii_lowercase + string.digits


def get_random_string(n, include_digits=True):
    choices_string = LETTERS_NUMBERS if include_digits else LETTERS
    return ''.join(
        random.choices(choices_string, k=n)
    )


class AccountTypeFactory(DjangoModelFactory):
    code = get_random_string(4)
    name = get_random_string(24)
    currency = get_random_string(3, include_digits=False)

    class Meta:
        model = AccountType
        django_get_or_create = ['code']
