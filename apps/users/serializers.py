from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.users.models import Profile, SupportMember

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'mobile', 'is_mobile_verified', 'user']
        extra_kwargs = {
            'user': {'write_only': True}
        }


class SupportMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMember
        fields = ['id', 'user']
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, **kwargs):
        has_profile = hasattr(instance, 'profile')
        has_support_member = hasattr(instance, 'supportmember')

        super().__init__(instance=instance, **kwargs)
        if has_profile:
            self.fields['profile'] = ProfileSerializer()
        if has_support_member:
            self.fields['supportmember'] = SupportMemberSerializer()

    class Meta:
        model = User
        fields = ['id', 'is_superuser', 'username', 'email',
                  'first_name', 'last_name', 'password', 'is_active',
                  'is_staff', 'is_supporter', 'date_joined', 'last_login',]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def to_internal_value(self, data):
        profile = data.get('profile', None)
        support_member = data.get('supportmember', None)
        ret = super().to_internal_value(data)
        if profile is not None:
            ret['profile'] = profile
        if support_member is not None:
            ret['supportmember'] = support_member
        return ret

    def create_attribute(self, serializer, data):
        ser = serializer(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()

    def create(self, validated_data):
        support_member_validated_data = validated_data.pop('supportmember', None)
        profile_validated_data = validated_data.pop('profile', None)
        user = User.objects.create_user(**validated_data)

        if support_member_validated_data is not None:
            support_member_validated_data['user'] = user.pk
            self.create_attribute(SupportMemberSerializer, support_member_validated_data)

        if profile_validated_data is not None:
            profile_validated_data['user'] = user.pk
            self.create_attribute(ProfileSerializer, profile_validated_data)

        return user
