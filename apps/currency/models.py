from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

import pycountry


def get_currencies():
    return [(i, i) for i in settings.CURRENCIES]


def get_countries():
    return [(country.name, country.name) for country in pycountry.countries]


class Currency(models.Model):
    code = models.CharField(
        _('code'), max_length=6, unique=True, choices=get_currencies())
    name = models.CharField(_('name'), max_length=24)
    symbol = models.CharField(_('symbol'), max_length=4, blank=True)
    country = models.CharField(_('country'), max_length=58, choices=get_countries())

    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code} : {self.name}'


class ExchangeRate(models.Model):
    source = models.CharField(
        _('source currency'), max_length=6, choices=get_currencies())
    destination = models.CharField(
        _('destination currency'), max_length=6, choices=get_currencies())
    rate = models.DecimalField(max_digits=5, decimal_places=3)

    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('source', 'destination'), )

    def __str__(self):
        return f'{self.source} -> {self.destination} : {self.rate}'

    @classmethod
    def get_rate(cls, source, destination):
        try:
            instance = cls.objects.get(source=source.upper(),
                                       destination=destination.upper(),
                                       is_active=True)
        except cls.DoesNotExist:
            return 1
        return instance.rate
