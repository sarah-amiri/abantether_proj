import json
import uuid

from bson import ObjectId
from django.http import Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.account import names
from apps.account.exceptions import (
    AccountsInvalidException,
    NotFoundAccountException,
    AmountInvalidException)
from apps.account.facade import transfer
from apps.account.permissions import AccountAccessPermission
from apps.account.models import Account, AccountType
from apps.account.serializers import (
    AccountSerializer,
    AccountTypeSerializer,
    AccountSummarySerializer,
    TransferSerializer, TransactionSerializer)
from apps.account.utils import get_accounts_by_name, find_documents_in_mongo
from apps.currency.models import ExchangeRate
from core.encoders import JSONEncoder


class AccountListCreateAPIView(ListCreateAPIView):
    serializer_class = AccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        accounts = Account.objects.all()

        currency = self.request.query_params.get('currency')
        if currency:
            accounts = accounts(currency=currency)

        if self.request.user.is_common_user:
            return accounts(user_id=self.request.user.id)
        return accounts


class AccountRetrieveAPIView(RetrieveAPIView):
    lookup_field = 'account_id'
    permission_classes = [AccountAccessPermission, ]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {'id': self.kwargs[lookup_url_kwarg]}
        try:
            obj = queryset(**filter_kwargs)[0]
        except IndexError:
            raise Http404

        self.check_object_permissions(self.request, obj)
        return obj


class AccountTypeListCreateAPIView(ListCreateAPIView):
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer


class DocumentAPIView(GenericViewSet):
    def get_options(self):
        user = self.request.user
        if user.is_common_user:
            options = {'$or': [{'source_account.user_id': user.id},
                               {'destination_account.user_id': user.id}]}
        else:
            options = {}
        return options

    def get_documents(self, collection_name):
        options = self.get_options()
        return find_documents_in_mongo(collection_name, **options)

    def get_object(self, collection_name):
        documents = self.get_documents(collection_name)
        return documents[0]


class TransferAPIView(DocumentAPIView):
    def get_accounts(self):
        source_account_name = self.request.data.get('source_account')
        destination_account_name = self.request.data.get('destination_account')
        if not (source_account_name or destination_account_name):
            raise AccountsInvalidException(_('Either source account or destination '
                                             'account name must be provided'))

        source_account, destination_account = get_accounts_by_name(source_account_name,
                                                                   destination_account_name)
        if not source_account or not destination_account:
            raise NotFoundAccountException(_('Source account or destination '
                                             'account does not exists'))

        if not (source_account.is_initial_account or
                source_account.has_access(self.request.user)):
            raise AccountsInvalidException(_('You don\'t have permission '
                                             'to complete this transfer'))

        return source_account, destination_account

    def get_transfer_type(self):
        if (self.request.data.get('source_account') and
                self.request.data.get('destination_account')):
            return 'transfer'
        elif self.request.data.get('source_account'):
            return 'withdraw'
        return 'deposit'

    def get_amount(self):
        amount = self.request.data.get('amount')
        if not amount or float(amount) <= 0:
            raise AmountInvalidException('Amount must be a positive number')
        return float(amount)

    def post(self, request, *args, **kwargs):
        try:
            source_account, destination_account = self.get_accounts()
        except AccountsInvalidException as e:
            return Response(dict(message=str(e)), status=status.HTTP_400_BAD_REQUEST)
        except NotFoundAccountException as e:
            return Response(dict(message=str(e)), status=status.HTTP_404_NOT_FOUND)

        source_currency, destination_currency = (source_account.currency,
                                                 destination_account.currency)
        rate = ExchangeRate.get_rate(source_currency, destination_currency)

        try:
            amount = self.get_amount()
        except AmountInvalidException as e:
            return Response(dict(message=str(e)), status=status.HTTP_400_BAD_REQUEST)

        data = {
            'source_account': AccountSummarySerializer(source_account).data,
            'destination_account': AccountSummarySerializer(destination_account).data,
            'amount': amount,
            'source_currency': source_currency,
            'destination_currency': destination_currency,
            'rate': rate,
            'transfer_type': self.get_transfer_type(),
            'description': request.data.get('description', None),
            'user': request.user.id,
            'reference': str(uuid.uuid4()),
            'created_time': timezone.now(),
            'payment_type': request.data.get('payment_type'),
            'payment_info': request.data.get('payment_info')
        }

        try:
            transfer(source_account, destination_account, data)
        except Exception as e:
            return Response(dict(message=str(e)), status=status.HTTP_400_BAD_REQUEST)

        data = json.loads(JSONEncoder().encode(data))
        return Response(data, status=status.HTTP_201_CREATED)

    def get(self, request):
        documents = self.get_documents(names.TRANSFER_COLLECTION)
        serializer = TransferSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionAPIView(DocumentAPIView):
    def get(self, request):
        documents = self.get_documents(names.TRANSACTION_COLLECTION)
        serializer = TransactionSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransferDetailAPIView(DocumentAPIView):
    def get_options(self):
        options = super().get_options()
        options.update({'_id': ObjectId(self.kwargs.get('transfer_id'))})
        return options

    def get_detail(self, request, transfer_id):
        try:
            instance = self.get_object(names.TRANSFER_COLLECTION)
        except IndexError:
            return Response(dict(message=_('Transfer with this transfer id not found')),
                            status=status.HTTP_404_NOT_FOUND)

        data = json.loads(JSONEncoder().encode(instance))
        return Response(data, status=status.HTTP_200_OK)

    def get_transactions(self, request, transfer_id):
        try:
            instance = self.get_object(names.TRANSFER_COLLECTION)
        except IndexError:
            return Response(dict(message=_('Transfer with this transfer id not found')),
                            status=status.HTTP_404_NOT_FOUND)

        options = {'$or': [{'account': instance.source_account.id},
                           {'account': instance.destination_account.id}]}
        transactions = find_documents_in_mongo(names.TRANSACTION_COLLECTION,
                                               **options)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionDetailAPIView(DocumentAPIView):
    def get_options(self):
        options = super().get_options()
        options.update({'_id': ObjectId(self.kwargs.get('transaction_id'))})
        return options

    def get_detail(self, request, transaction_id):
        try:
            instance = self.get_object(names.TRANSACTION_COLLECTION)
        except IndexError:
            return Response(dict(message=_('Transaction with this transaction id not found')),
                            status=status.HTTP_404_NOT_FOUND)

        data = json.loads(JSONEncoder().encode(instance))
        return Response(data, status=status.HTTP_200_OK)


transfer_view = TransferAPIView.as_view({'get': 'get', 'post': 'post'})
transaction_view = TransactionAPIView.as_view({'get': 'get'})
transfer_detail_view = TransferDetailAPIView.as_view({'get': 'get_detail'})
transfer_transactions_view = TransferDetailAPIView.as_view({'get': 'get_transactions'})
transaction_detail_view = TransactionDetailAPIView.as_view({'get': 'get_detail'})
