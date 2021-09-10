from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.utils import connect_to_mongo

from apps.account.exceptions import (
    AccountException, InsufficientBalanceException
)
from apps.account.names import (
    TRANSFER_COLLECTION, TRANSACTION_COLLECTION
)


def transfer(source_account, destination_account, data):
    source = data.get('source_account')
    destination = data.get('destination_account')
    amount = data.get('amount')

    if source.get('id') == destination.get('id'):
        raise AccountException(
            _('Source account and destination account must be different'))

    if source.get('balance') - amount < 0 and source.get('balance_limit') != -1:
        raise InsufficientBalanceException(
            _('There is not sufficient money in source account'))

    client, db = connect_to_mongo()

    transfer_collection = db[TRANSFER_COLLECTION]
    transaction_collection = db[TRANSACTION_COLLECTION]

    transfer_id = transfer_collection.insert(data)

    source_transaction = {
        'transfer': str(transfer_id),
        'account': source,
        'amount': -amount,
        'created_time': timezone.now()
    }
    destination_transaction = {
        'transfer': str(transfer_id),
        'account': destination,
        'amount': amount,
        'created_time': source_transaction.get('created_time')
    }
    transaction_collection.insert_many([source_transaction, destination_transaction])

    client.close()

    source_account.save()
    destination_account.save()

    return transfer_id
