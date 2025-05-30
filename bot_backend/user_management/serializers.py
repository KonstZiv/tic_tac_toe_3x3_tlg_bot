from rest_framework import serializers

from user_management.models import User, TgUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name']


class TgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = ['id', 'tg_first_name', 'tg_last_name', 'tg_username', 'is_bot', 'language_code',
                  'is_premium', 'added_to_attachment_menu', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PlayerSerializer(serializers.Serializer):
    """Серіалізатор для поліморфного гравця (User або TgUser)."""
    id = serializers.IntegerField()
    type = serializers.CharField()  # 'user' або 'tguser'
    email = serializers.EmailField(source='user.email', allow_null=True)
    username = serializers.CharField(source='user.username', allow_null=True)
    first_name = serializers.CharField(source='user.first_name', allow_null=True)
    last_name = serializers.CharField(source='user.last_name', allow_null=True)
    tg_first_name = serializers.CharField(allow_null=True)
    tg_last_name = serializers.CharField(allow_null=True)
    tg_username = serializers.CharField(allow_null=True)
    is_bot = serializers.BooleanField(allow_null=True)
    language_code = serializers.CharField(allow_null=True)


    def to_representation(self, instance):
        if isinstance(instance, User):
            return UserSerializer(instance).data
        elif isinstance(instance, TgUser):
            return TgUserSerializer(instance).data
        return None