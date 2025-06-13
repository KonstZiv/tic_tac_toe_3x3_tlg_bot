from django.db.models import TextChoices
from rest_framework import serializers

from user_management.models import User, TgUser


class PossibleUserTypes(TextChoices):
    WEBUSER = "User", "User"
    TGUSER = "TgUser", "TgUser"


class UserSerializer(serializers.ModelSerializer):
    user_content_type = serializers.ChoiceField(
        choices=PossibleUserTypes.values,
        default=PossibleUserTypes.WEBUSER,
        help_text=f"User type: {PossibleUserTypes.values}",
    )

    class Meta:
        model = User
        fields = [
            "user_content_type",
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id"]


class TgUserSerializer(serializers.ModelSerializer):
    user_content_type = serializers.ChoiceField(
        choices=PossibleUserTypes.values,
        default=PossibleUserTypes.TGUSER,
        help_text=f"User type: {PossibleUserTypes.values}",
    )

    class Meta:
        model = TgUser
        fields = [
            "user_content_type",
            "id",
            "tg_first_name",
            "tg_last_name",
            "tg_username",
            "is_bot",
            "language_code",
            "is_premium",
            "added_to_attachment_menu",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "id",
            "is_premium",
            "added_to_attachment_menu",
        ]


class UnknownUserSerializer(serializers.Serializer):

    user_content_type = serializers.ChoiceField(
        allow_null=True,
        default=None,
        choices=PossibleUserTypes.values,
        help_text=f"User type: {PossibleUserTypes.values}",
    )
    user_object_id = serializers.IntegerField(
        allow_null=True,
        default=None,
        help_text="ID of the user object (User or TgUser).",
    )
