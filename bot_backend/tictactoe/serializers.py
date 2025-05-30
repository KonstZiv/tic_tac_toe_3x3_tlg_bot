from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework import serializers

from user_management.models import TgUser
from user_management.serializers import PlayerSerializer
from .models import TicTacToeProposition


class TicTacToePropositionSerializer(serializers.ModelSerializer):
    player1 = PlayerSerializer(read_only=True)
    player2 = PlayerSerializer(read_only=True, allow_null=True)
    deep_links = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TicTacToeProposition
        fields = [
            'id', 'player1', 'player2', 'player1_first', 'player1_sign', 'player2_sign',
            'created_at', 'accepted_at', 'status', 'expires_at', 'deep_links'
        ]
        read_only_fields = ['created_at', 'player1', 'accepted_at', 'status']

    def validate_expires_at(self, value):
        """Перевіряє, що expires_at не раніше поточного часу."""
        if value and value < timezone.now():
            raise serializers.ValidationError("Expiration date cannot be in the past.")
        return value

    def validate(self, data):
        """Додаткова валідація для створення/оновлення."""
        if 'player2_sign' in data and 'player1_sign' in data:
            if data['player1_sign'] == data['player2_sign']:
                raise serializers.ValidationError("Player 1 and Player 2 must have different signs.")
        return data

    def create(self, validated_data):
        """Створює пропозицію з player1, визначеним із контексту."""
        print(f"Context: {self.context}")
        request = self.context.get('request')
        tguser_id = self.context.get('tguser_pk')
        content_type = ContentType.objects.get_for_model(TgUser)

        proposition = TicTacToeProposition(
            player1_content_type=content_type,
            player1_object_id=tguser_id,
            **validated_data
        )
        proposition.save()
        return proposition

    def get_deep_links(self, obj):
        """Повертає глибокі посилання для Telegram і веб-застосунку."""
        telegram_link = f"https://t.me/YourBotName?start=proposition_{obj.id}"
        web_link = f"https://yourapp.com/tictactoe/proposition/{obj.id}"
        return {
            'telegram': telegram_link,
            'web': web_link
        }
