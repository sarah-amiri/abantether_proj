from django.urls import path

from apps.account.views import (
    AccountListCreateAPIView, AccountRetrieveAPIView, AccountTypeListCreateAPIView,
    transfer_view, transaction_view, transfer_detail_view, transfer_transactions_view,
    transaction_detail_view
)

urlpatterns = [
    path('account/', AccountListCreateAPIView.as_view(), name='account-create-list'),
    path('account/<str:account_id>/', AccountRetrieveAPIView.as_view(), name='account-detail'),
    path('account-types/', AccountTypeListCreateAPIView.as_view(), name='account-type-create-list'),

    # path('accounts/<int:user_id>/transactions/'),
    # path('accounts/<int:user_id>/transfers/'),
    #
    path('transfer/', transfer_view, name='transfer'),
    path('transaction/', transaction_view, name='transaction'),
    path('transaction/<str:transaction_id>/',
         transaction_detail_view,
         name='transaction-detail'),
    path('transfer/<str:transfer_id>/',
         transfer_detail_view,
         name='transfer-detail'),
    path('transfer/<str:transfer_id>/transactions/',
         transfer_transactions_view,
         name='transfer-transactions'),
    # path('transfer/<transaction_id>/transactions/')
]
