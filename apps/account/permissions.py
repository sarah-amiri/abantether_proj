from rest_framework.permissions import BasePermission


class AccountAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (obj.user_id == request.user.id or
                request.user.is_supporter or
                request.user.is_superuser)
