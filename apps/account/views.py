import uuid

from django.http import Http404
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.account.permissions import AccountAccessPermission
from apps.account.models import Account, AccountType
from apps.account.serializers import AccountSerializer, AccountTypeSerializer, AccountSummarySerializer
from apps.account.utils import get_accounts_by_name
from apps.currency.models import ExchangeRate
from core.utils import connect_to_mongo


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


class TransferAPIView(APIView):
    def get_accounts(self):
        message = None
        source_account_name = self.request.data.get('source_account')
        destination_account_name = self.request.data.get('destination_account')
        if not (source_account_name or destination_account_name):
            message = 'Either source account or destination account name must be provided'
            return None, None, message

        source_account, destination_account = get_accounts_by_name(source_account_name, destination_account_name)
        if not source_account or not destination_account:
            message = 'Source account or destination account does not exists'

        return source_account, destination_account, message

    def get_transfer_type(self):
        if self.request.data.get('source_account') and self.request.data.get('destination_account'):
            return 'transfer'
        elif self.request.data.get('source_account'):
            return 'withdraw'
        return 'deposit'

    def get_amount(self):
        amount = self.request.data.get('amount')
        if not amount:
            message = 'Amount must be provided'
            return amount, message

        amount = float(amount)
        if amount <= 0:
            message = 'Amount must be a positive number'
            return amount, message
        return amount, None

    def post(self, request, *args, **kwargs):
        source_account, destination_account, message = self.get_accounts()
        if message:
            return Response(dict(message=message),
                            status=status.HTTP_400_BAD_REQUEST)
        source_currency, destination_currency = source_account.currency, destination_account.currency
        rate = ExchangeRate.get_rate(source_currency, destination_currency)

        amount, message = self.get_amount()
        if message:
            return Response(dict(message=message),
                            status=status.HTTP_400_BAD_REQUEST)

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

        client, db = connect_to_mongo()
        collection = db['transfer']
        collection.insert(data)
        client.close()

        return Response(status=status.HTTP_201_CREATED)
