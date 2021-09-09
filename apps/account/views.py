from django.http import Http404

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
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

        if self.request.user.is_common_user:
            return accounts(user_id=self.request.user.id)
        return accounts


class AccountRetrieveAPIView(RetrieveAPIView):
    lookup_field = 'account_id'
    serializer_class = AccountSerializer

    def get_queryset(self):
        queryset = Account.objects.all()
        if not self.request.user.is_common_user:
            return queryset
        return queryset(user_id=self.request.user.id)

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
