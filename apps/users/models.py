from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    is_supporter = models.BooleanField(
        _('supporter status'),
        default=False,
        help_text=_('Designates whether user can log in as site supporter.')
    )

    @property
    def is_common_user(self):
        return not self.is_supporter and not self.is_superuser


class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'), on_delete=models.CASCADE)
    mobile = models.CharField(_('user mobile'), max_length=11, blank=True)
    is_mobile_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'Profile ({self.id}) : {self.user.username}'


class SupportMember(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'), on_delete=models.CASCADE)

    def __str__(self):
        return f'Support Member ({self.id}) : {self.user.username}'
