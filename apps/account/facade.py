import logging

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.account.exceptions import (
    AccountException, InsufficientBalanceException
)
from apps.account.names import (
    TRANSFER_COLLECTION, TRANSACTION_COLLECTION
)
from core.utils import connect_to_mongo

logger = logging.getLogger('transfers')


def transfer(source_account, destination_account, data):
    source = data.get('source_account')
    destination = data.get('destination_account')
    amount = data.get('amount')

    message = '[Transfer] - Transfer of %.2f from account %s to account %s' % (
        amount, source.get('name'), destination.get('name'))

    if source.get('id') == destination.get('id'):
        error_message = 'Source account and destination account must be different'
        logger.warning('%s - [Failed] %s' % (message, error_message))
        raise AccountException(_(error_message))

    if source.get('balance') - amount < 0 and not source_account.is_initial_account:
        error_message = 'There is not sufficient money in source account'
        logger.error('%s - [Failed] %s' % (message, error_message))
        raise InsufficientBalanceException(_(error_message))

    client, db = connect_to_mongo()

    transfer_collection = db[TRANSFER_COLLECTION]
    transaction_collection = db[TRANSACTION_COLLECTION]

    transfer_id = transfer_collection.insert(data)

    success_message = f'Transfer {transfer_id} is complete successfully'
    logger.info('%s - [Success] %s' % (message, success_message))

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
