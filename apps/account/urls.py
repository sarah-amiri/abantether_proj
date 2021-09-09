from django.urls import path

from apps.account.views import AccountListCreateAPIView

urlpatterns = [
    path('account/', AccountListCreateAPIView.as_view(), name='account-create-list'),
    # path('accounts/<string:currency>/'),
    # path('accounts/<int:user_id>/transactions/'),
    # path('accounts/<int:user_id>/transfers/'),
    # path('account/<int:account_id>/'),
    #
    # path('transfer/'),
    # path('transactions/'),
    # path('transfers/'),
    # path('transaction/<transaction_id>/'),
    # path('transfer/<transfer_id>/'),
    # path('transfer/<transaction_id>/transactions/')
]
