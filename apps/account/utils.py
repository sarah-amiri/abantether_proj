from apps.account.models import Account
from apps.account.names import initial_account_name, TRANSACTION_COLLECTION
from core.utils import connect_to_mongo


def get_accounts_by_name(source_account_name=None, destination_account_name=None):
    if source_account_name and destination_account_name:
        source_account = Account.objects(
            name=source_account_name, status='Active').first()
        destination_account = Account.objects(
            name=destination_account_name, status='Active').first()
        return source_account, destination_account

    if source_account_name:
        try:
            source_account = Account.objects(
                name=source_account_name, status='Active')[0]
            currency = source_account.currency
            destination_account = Account.objects(
                name=initial_account_name.format(currency), status='Active'
            )[0]
        except (IndexError, AttributeError):
            source_account, destination_account = None, None

    else:
        try:
            destination_account = Account.objects(
                name=destination_account_name, status='Active')[0]
            currency = destination_account.currency
            source_account = Account.objects(
                name=initial_account_name.format(currency), status='Active'
            )[0]
        except (IndexError, AttributeError):
            source_account, destination_account = None, None

    return source_account, destination_account


def find_account_balance(account_name):
    client, db = connect_to_mongo()

    collection = db[TRANSACTION_COLLECTION]

    result = collection.aggregate([
        {'$match': {'account.name': account_name}},
        {'$group': {'_id': None, 'sum': {'$sum': '$amount'}}}
    ])
    client.close()

    try:
        return result.next()['sum']
    except StopIteration:
        return 0
