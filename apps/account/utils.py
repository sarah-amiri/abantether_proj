from apps.account.models import Account
from apps.account.names import initial_account_name


def get_accounts_by_name(source_account_name=None, destination_account_name=None):
    if source_account_name and destination_account_name:
        source_account = Account.objects(name=source_account_name).first()
        destination_account = Account.objects(name=destination_account_name).first()
        return source_account, destination_account

    if source_account_name:
        try:
            source_account = Account.objects(name=source_account_name)[0]
            currency = source_account.currency
            destination_account = Account.objects(name=initial_account_name.format(currency))[0]
        except (IndexError, AttributeError):
            source_account, destination_account = None, None

    else:
        try:
            destination_account = Account.objects(name=destination_account_name)[0]
            currency = destination_account.currency
            source_account = Account.objects(name=initial_account_name.format(currency))[0]
        except (IndexError, AttributeError):
            source_account, destination_account = None, None

    return source_account, destination_account
