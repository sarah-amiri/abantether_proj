from django.contrib import admin
from django.contrib.admin import register

from apps.users.models import Profile, SupportMember


@register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@register(SupportMember)
class SupportMemberAdmin(admin.ModelAdmin):
    pass
