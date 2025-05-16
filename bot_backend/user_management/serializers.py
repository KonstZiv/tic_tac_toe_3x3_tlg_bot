from rest_framework import serializers

from .models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = ['id', 'tg_id', 'tg_first_name', 'tg_last_name', 'tg_username', 'is_bot', 'language_code',
                  'is_premium', 'added_to_attachment_menu', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
