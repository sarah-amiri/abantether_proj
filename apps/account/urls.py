from django.urls import path

from apps.account.views import (
    AccountListCreateAPIView,
    AccountRetrieveAPIView
)

urlpatterns = [
    path('account/', AccountListCreateAPIView.as_view(), name='account-create-list'),
    path('account/<str:account_id>/', AccountRetrieveAPIView.as_view(), name='account-detail'),
    # path('accounts/<int:user_id>/transactions/'),
    # path('accounts/<int:user_id>/transfers/'),
    #
    # path('transfer/'),
    # path('transactions/'),
    # path('transfers/'),
    # path('transaction/<transaction_id>/'),
    # path('transfer/<transfer_id>/'),
    # path('transfer/<transaction_id>/transactions/')
]
