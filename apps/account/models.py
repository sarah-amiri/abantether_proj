from enum import Enum
import mongoengine

from django.conf import settings
from django.utils import timezone

mongoengine.connect(
    db=settings.MONGO_DB,
    host=settings.MONGO_HOST,
    username=settings.MONGO_USER,
    password=settings.MONGO_PASS
)


class AccountType(mongoengine.Document):
    code = mongoengine.StringField(max_length=8, required=True, unique=True)
    name = mongoengine.StringField(max_length=64, required=True)
    currency = mongoengine.StringField(max_length=8, required=True, unique_with='name')
    is_active = mongoengine.BooleanField(default=True)
    created_time = mongoengine.DateTimeField(required=True)

    def __str__(self):
        return f'{self.code}: {self.name}, {self.currency}'

    @classmethod
    def create_account_type(cls, code, name, currency):
        obj = cls(
            code=code, name=name, currency=currency,
            created_time=timezone.now()
        )
        return obj.save()


class AccountStatus(Enum):
    STATUS_ACTIVE = 'Active'
    STATUS_OPENED = 'Opened'
    STATUS_CLOSED = 'Closed'
    STATUS_FREEZE = 'Freeze'


class Account(mongoengine.Document):
    name = mongoengine.StringField(max_length=225, unique=True, required=True)
    description = mongoengine.StringField()
    user_id = mongoengine.IntField(required=True)
    user_username = mongoengine.StringField(max_length=64, required=True)
    account_type = mongoengine.ReferenceField(AccountType, required=True)
    currency = mongoengine.StringField(max_length=8, default='IRR', required=True)
    balance_limit = mongoengine.FloatField(default=0.00)
    balance = mongoengine.FloatField(default=0.00)
    status = mongoengine.EnumField(AccountStatus, default=AccountStatus.STATUS_OPENED)

    created_time = mongoengine.DateTimeField(required=True)
    modified_time = mongoengine.DateTimeField(required=True)
    date_activated = mongoengine.DateTimeField()
    date_closed = mongoengine.DateTimeField()

    def __str__(self):
        return self.name

    def save(
        self,
        force_insert=False,
        validate=True,
        clean=True,
        write_concern=None,
        cascade=None,
        cascade_kwargs=None,
        _refs=None,
        save_condition=None,
        signal_kwargs=None,
        **kwargs,
    ):
        if not self.name:
            self.name = f'{self.user_username}_{self.currency}'
        self.balance = self._balance()
        return super().save(force_insert=force_insert,
                            validate=validate,
                            clean=clean,
                            write_concern=write_concern,
                            cascade=cascade,
                            cascade_kwargs=cascade_kwargs,
                            _refs=_refs,
                            save_condition=save_condition,
                            signal_kwargs=signal_kwargs,
                            **kwargs)

    def _balance(self):
        from apps.account.utils import find_account_balance
        return find_account_balance(self.name)

    @property
    def is_active(self):
        return self.status == AccountStatus.STATUS_ACTIVE

    @property
    def is_initial_account(self):
        return self.balance_limit < 0

    def has_access(self, user):
        return self.user_id == user.id or not user.is_common_user

    def activate_accounts(self):
        self.status = AccountStatus.STATUS_ACTIVE
        self.date_activated = timezone.now()
        self.modified_time = timezone.now()
        self.save()

    def close_account(self):
        self.status = AccountStatus.STATUS_CLOSED
        self.date_closed = timezone.now()
        self.modified_time = timezone.now()
        self.save()

    def freeze_account(self):
        self.status = AccountStatus.STATUS_FREEZE
        self.modified_time = timezone.now()
        self.save()

    @classmethod
    def create_account(cls, user_id, user_username,
                       name, account_type, **kwargs):
        obj = cls(user_id=user_id, user_username=user_username,
                  name=name, account_type=account_type,
                  created_time=timezone.now(), modified_time=timezone.now())

        for attr in kwargs:
            setattr(obj, attr, kwargs[attr])

        return obj.save()
