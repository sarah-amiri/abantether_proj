from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import Profile, SupportMember

User = get_user_model()


@receiver(post_save, sender=User)
def create_users_models(sender, instance, *args, **kwargs):
    if instance.is_supporter:
        SupportMember.objects.create(user=instance)
    elif not instance.is_staff:
        Profile.objects.create(user=instance)
