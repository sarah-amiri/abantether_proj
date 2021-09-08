import pytest

from apps.account.models import AccountType
from apps.account.tests.factories import AccountTypeFactory


@pytest.fixture
def account_type() -> AccountType:
    return AccountTypeFactory()
