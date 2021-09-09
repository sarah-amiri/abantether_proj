from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from apps.account.serializers import Account
from apps.account.serializers import AccountSerializer


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

        if self.request.user.is_superuser or self.request.user.is_supporter:
            return accounts
        return accounts(user_id=self.request.user.id)
