from django.contrib import admin
from django.contrib.admin import register

from apps.currency.models import Currency, ExchangeRate


@register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    pass
