from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from user_management.models import TgUser, User
from user_management.serializers import (
    UnknownUserSerializer,
    UserSerializer,
    TgUserSerializer,
)
from .models import TicTacToeProposition


class TicTacToePropositionSerializer(serializers.ModelSerializer):
    """
    A basic serializer for working with TicTacToeProposition objects.
    """

    deep_links = serializers.SerializerMethodField(
        read_only=True,
        help_text="Deep links to access the offer via Telegram or the web.",
    )

    class Meta:
        model = TicTacToeProposition
        fields = "__all__"
        read_only_fields = ["created_at", "status", "id"]

    def validate_expires_at(self, value):
        """Checks that expires_at is not in the past."""
        if value and value < timezone.now():
            raise serializers.ValidationError("Expiration date cannot be in the past.")
        return value

    def validate(self, data):
        """Checks that the player signs (player1_sign, player2_sign) are different, if specified."""
        if (
            data["player1_sign"]
            and data["player1_sign"] not in self.Meta.model.PossibleSign.values
        ):
            raise serializers.ValidationError(
                f"Invalid player1_sign: {data['player1_sign']}. "
                f"Must be one of {list(self.Meta.model.PossibleSign.values())}."
            )
        if (
            data.get("player2_sign")
            and data["player2_sign"] not in self.Meta.model.PossibleSign.values
        ):
            raise serializers.ValidationError(
                f"Invalid player2_sign: {data['player2_sign']}. "
                f"Must be one of {list(self.Meta.model.PossibleSign.values())}."
            )
        if data.get("player2_sign") or data.get("player1_sign"):
            if data["player1_sign"] == data["player2_sign"]:
                raise serializers.ValidationError(
                    "Player 1 and Player 2 must have different signs."
                )
        return data

    def create(self, validated_data):
        """Creates a TicTacToeProposition with player1 identified from the context."""
        player1_object_id = self.context.get("player1_object_id")
        player1_content_type = ContentType.objects.get_for_model(TgUser)

        proposition = TicTacToeProposition(
            player1_content_type=player1_content_type,
            player1_object_id=player1_object_id,
            **validated_data,
        )
        proposition.save()
        return proposition

    def get_deep_links(self, obj) -> dict[str, str]:
        """Returns deep links for Telegram and the web app."""
        telegram_link = f"https://t.me/YourBotName?start=proposition_{obj.id}"
        web_link = f"https://yourapp.com/tictactoe/proposition/{obj.id}"
        return {"telegram": telegram_link, "web": web_link}


class TicTacToePropositionGetSerializer(TicTacToePropositionSerializer):
    """Serializer for read operations (GET requests). Adds player details (player1, player2)."""

    class Meta(TicTacToePropositionSerializer.Meta):
        fields = [
            "id",
            "player1",
            "player2",
            "player1_first",
            "player1_sign",
            "player2_sign",
            "created_at",
            "accepted_at",
            "status",
            "expires_at",
            "deep_links",
        ]
        read_only_fields = ["created_at", "player1", "accepted_at", "status", "id"]

    def get_player_serializer(self, player_instance, content_type):
        """Returns the appropriate serializer depending on content_type."""
        if player_instance is None:
            return UnknownUserSerializer
        user_ct = ContentType.objects.get_for_model(User)
        tguser_ct = ContentType.objects.get_for_model(TgUser)
        if content_type == user_ct:
            return UserSerializer
        elif content_type == tguser_ct:
            return TgUserSerializer
        return UnknownUserSerializer

    def to_representation(self, instance):
        # Get a standard representation
        data = super().to_representation(instance)

        # Define serializer for player1
        player1_serializer = self.get_player_serializer(
            instance.player1, instance.player1_content_type
        )
        data["player1"] = (
            player1_serializer(instance.player1, context=self.context).data
            if instance.player1
            else None
        )

        # Define serializer for player2
        player2_serializer = self.get_player_serializer(
            instance.player2, instance.player2_content_type
        )
        data["player2"] = (
            player2_serializer(instance.player2, context=self.context).data
            if instance.player2
            else UnknownUserSerializer().data
        )

        return data


class TicTacToePropositionPostSerializer(TicTacToePropositionSerializer):
    """
    Serializer for create/update operations (POST/PUT/PATCH).
    Includes fields for player2 and game settings.
    """

    player2_content_type_id = serializers.IntegerField(
        help_text="Content type ID for player2 (e.g., TgUser).",
        required=False,
        allow_null=True,
    )
    player2_object_id = serializers.IntegerField(
        help_text="Object ID for player2 (e.g., TgUser ID).",
        required=False,
        allow_null=True,
    )

    class Meta(TicTacToePropositionSerializer.Meta):
        fields = [
            "id",
            "player2_content_type_id",
            "player2_object_id",
            "player1_first",
            "player1_sign",
            "player2_sign",
            "expires_at",
            "deep_links",
            "status",
            "created_at",
        ]
        read_only_fields = ["deep_links", "id", "created_at", "status"]

    def validate(self, data):
        """
        Перевіряє, що player2_content_type_id і player2_object_id вказані разом або обидва відсутні.
        """
        player2_content_type_id = data.get("player2_content_type_id")
        player2_object_id = data.get("player2_object_id")
        if (player2_content_type_id and not player2_object_id) or (
            not player2_content_type_id and player2_object_id
        ):
            raise serializers.ValidationError(
                "Both player2_content_type_id and player2_object_id must be provided or both omitted."
            )
        return super().validate(data)

    def create(self, validated_data):
        """
        Створює пропозицію з player1, визначеним із контексту, і player2 із validated_data (якщо є).
        """
        player1_object_id = self.context.get("player1_object_id")
        player1_content_type = self.context.get("player1_content_type")

        if not player1_object_id or not player1_content_type:
            raise serializers.ValidationError(
                "Player1 content type and object ID must be provided in context."
            )

        # Отримуємо player2 з validated_data
        player2_content_type_id = validated_data.pop("player2_content_type_id", None)
        player2_object_id = validated_data.pop("player2_object_id", None)

        if (player2_content_type_id and not player2_object_id) or (
            not player2_content_type_id and player2_object_id
        ):
            raise serializers.ValidationError(
                "Both player2_content_type_id and player2_object_id are required."
            )

        proposition = TicTacToeProposition(
            player1_content_type=player1_content_type,
            player1_object_id=player1_object_id,
            player2_content_type_id=player2_content_type_id,
            player2_object_id=player2_object_id,
            **validated_data,
        )
        proposition.save()
        return proposition


@extend_schema_serializer(
    component_name="Поле для обробки списків значень, розділених комами, з валідацією через choices.",
)
class CommaSeparatedChoiceListField(serializers.ListField):
    """
    Кастомне поле для обробки comma-separated значень у query-параметрах.
    Валідує кожен елемент як ChoiceField із заданими choices.
    """

    def __init__(self, choices, **kwargs):
        self.choices = choices
        super().__init__(child=serializers.ChoiceField(choices=choices), **kwargs)

    def to_internal_value(self, data):
        # Якщо data є списком, обробляємо кожен елемент
        if isinstance(data, list):
            # Розбиваємо кожен елемент, якщо він містить коми
            items = []
            for item in data:
                if isinstance(item, str):
                    items.extend([i.strip() for i in item.split(",") if i.strip()])
                else:
                    items.append(item)
            data = items
        # Якщо data є рядком, розбиваємо його за комами
        elif isinstance(data, str):
            data = [item.strip() for item in data.split(",") if item.strip()]
        return super().to_internal_value(data)


@extend_schema_serializer(
    component_name="Серіалізатор для фільтрації GET-запитів до пропозицій гри.",
)
class TicTacToePropositionFilterSerializer(serializers.Serializer):
    """
    Серіалізатор для валідації GET-параметрів при фільтрації пропозицій.
    Підтримує фільтрацію за статусом, роллю гравця та терміном дії.
    """

    statuses = CommaSeparatedChoiceListField(
        choices=[s[0] for s in TicTacToeProposition._meta.get_field("status").choices],
        required=False,
        allow_empty=True,
        help_text=(
            "Filter by proposition status (comma-separated - e.g., '?statuses=pending,accepted,declined'). "
            "If not specified - values for all statuses are returned."
        ),
    )
    is_player1 = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text=(
            "Filter by whether the user is player1 (true) or player2 (false). "
            "If not specified - returns values where user is either player1 or player2"
        ),
    )
    expired = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text=(
            "Filter by whether the proposition is expired (true) or not (false). "
            "If not specified - returns values for both expired and not expired propositions."
        ),
    )
