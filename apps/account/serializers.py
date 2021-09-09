from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from apps.account.models import AccountType, Account, AccountStatus


class AccountTypeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8)
    name = serializers.CharField(max_length=64)
    currency = serializers.CharField(max_length=8)
    is_active = serializers.BooleanField(required=False)
    created_time = serializers.DateTimeField(read_only=True)

    class Meta:
        extra_kwargs = {
            'code': {
                'validators': [UniqueValidator(queryset=AccountType.objects.all())]
            },
            'currency': {
                'validators': [UniqueTogetherValidator(queryset=AccountType.objects.all(),
                               fields=['name'])]
            },
        }

    def create(self, validated_data):
        instance = AccountType.create_account_type(
            validated_data['code'],
            validated_data['name'],
            validated_data['currency']
        )
        return instance

    def update(self, instance, validated_data):
        pass


class AccountSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=225)
    description = serializers.CharField(max_length=225, required=False)
    user_id = serializers.IntegerField()
    user_username = serializers.CharField(max_length=64)
    account_type = serializers.PrimaryKeyRelatedField(queryset=AccountType.objects.all())
    currency = serializers.CharField(max_length=8, required=False)
    balance_limit = serializers.FloatField(required=False)
    balance = serializers.FloatField(read_only=True)
    status = serializers.ChoiceField(choices=AccountStatus, required=False)
    created_time = serializers.DateTimeField(read_only=True)
    modified_time = serializers.DateTimeField(read_only=True)
    date_activated = serializers.DateTimeField(required=False)
    date_closed = serializers.DateTimeField(required=False)

    class Meta:
        extra_kwargs = {
            'name': {
                'validators': [UniqueValidator(queryset=Account.objects.all())]
            }
        }

    def validate_name(self, name):
        try:
            Account.objects(name=name)[0]
        except IndexError:
            return name
        raise ValidationError(_('Account with that name already exists'))

    def get_code_account_type(self, account_type_code):
        return AccountType.objects(code=account_type_code).first()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        account_type = AccountType.objects(id=ret['account_type']).first()
        ret['account_type'] = AccountTypeSerializer(account_type).data
        ret['status'] = ret['status'].value
        return ret

    def to_internal_value(self, data):
        account_type_code = data.get('account_type_code')
        account_type_obj = self.get_code_account_type(account_type_code)
        user = self.context['request'].user

        new_data = {
            'account_type': account_type_obj.id if account_type_obj else None,
            'currency': account_type_obj.currency if account_type_obj else None,
            'user_id': user.pk,
            'user_username': user.username
        }
        new_data.update({
            'name': f'{user.username}_{new_data["currency"]}',
        })
        return super().to_internal_value(new_data)

    def create(self, validated_data):
        instance = Account.create_account(
            validated_data.pop('user_id'),
            validated_data.pop('user_username'),
            validated_data.pop('name'),
            validated_data.pop('account_type'),
            **validated_data
        )
        return instance

    def update(self, instance, validated_data):
        pass



