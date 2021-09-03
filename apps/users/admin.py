from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth import get_user_model

from apps.users.models import Profile, SupportMember


@register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_supporter', 'is_active', )


@register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@register(SupportMember)
class SupportMemberAdmin(admin.ModelAdmin):
    pass
