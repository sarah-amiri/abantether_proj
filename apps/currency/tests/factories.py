import random
import string

from apps.currency.models import Currency

from factory.django import DjangoModelFactory
from factory import Faker


def get_random_string(length=1, include_digits=True):
    strings = string.ascii_uppercase
    if include_digits:
        strings += string.digits
    return ''.join(random.choices(strings, k=length))


class CurrencyFactory(DjangoModelFactory):
    code = get_random_string(3, include_digits=False)
    name= Faker("name")

    class Meta:
        model = Currency
        django_get_or_create = ['code']
