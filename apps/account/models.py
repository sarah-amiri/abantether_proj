from decimal import Decimal as D

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.currency.models import Currency

User = get_user_model()


class AccountType(models.Model):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(_('name'), max_length=64)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('name', 'currency'), )

    def __str__(self):
        return self.code


class Account(models.Model):
    STATUS_ACTIVE = 'Active'
    STATUS_OPENED = 'Opened'
    STATUS_CLOSED = 'Closed'
    STATUS_FREEZE = 'Freeze'
    ACCOUNT_STATUS_CHOICES = (
        (STATUS_ACTIVE, _('Account is active and can be used to transfer money')),
        (STATUS_OPENED, _('Account is opened but is not active yet')),
        (STATUS_CLOSED, _('Account is closed and cannot be active anymore')),
        (STATUS_FREEZE, _('Account is inactive now but will be active or closed later'))
    )

    name = models.CharField(_('name'), max_length=225, unique=True)
    description = models.TextField(blank=True)
    primary_user = models.ForeignKey(
        User, related_name='primary_accounts', on_delete=models.CASCADE)
    other_users = models.ManyToManyField(User, related_name='secondary_accounts')
    account_type = models.ForeignKey(
        AccountType, related_name='accounts', on_delete=models.CASCADE)
    balance_limit = models.DecimalField(
        max_digits=4, decimal_places=2, default=D('0.00'), null=True,
        help_text=_('Balance limit is 0.00 by default. '
                    'Set to null, it means there is no limit for balance.'))
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=D('0.00'))
    status = models.CharField(
        max_length=8, choices=ACCOUNT_STATUS_CHOICES, default=STATUS_OPENED)

    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    date_activated = models.DateTimeField(blank=True)
    date_closed = models.DateTimeField(blank=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.balance = self._balance()
        return super().save(force_insert=force_insert, force_update=force_update,
                            using=using, update_fields=update_fields)

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def activate_account(self):
        self.status = self.STATUS_ACTIVE
        self.date_activated = timezone.now()
        self.save()

    def close_account(self):
        self.status = self.STATUS_CLOSED
        self.date_closed = timezone.now()
        self.save()

    def _balance(self):
        # Todo: calculate balance based on transactions using aggregation
        # for now return balance
        return self.balance
