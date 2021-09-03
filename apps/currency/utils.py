from decimal import Decimal as D

from apps.currency.models import ExchangeRate


def exchange_price(price, source_currency, destination_currency):
    rate = ExchangeRate.get_rate(source_currency, destination_currency)
    new_price = D(rate) * D(price)
    return D(f'{new_price}:.2f')
