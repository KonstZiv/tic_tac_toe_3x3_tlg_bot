from datetime import timedelta, datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def get_data_expired(
    timestamp: datetime | None = None, period: timedelta = timedelta(days=7)
) -> datetime:
    """Returns the datetime of the offer expiration date (7 days from the current date by default).
    Parameters:
    - timestamp: datetime (optional) - the date from which the period is calculated (by default - the current date)
    - period: timedelta (optional) - the time interval from the timestamp to form the final datetime.
    By default, 7 days.
    """
    if timestamp is None:
        timestamp = timezone.now()
    return timestamp + period


class TicTacToeProposition(models.Model):
    """
    Tic-tac-toe game offer model.
    Stores information about players, game settings, and offer status.
    """

    class PossibleStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        ACCEPTED = "accepted", _("Accepted")
        DECLINED = "declined", _("Declined")
        INCOMPLETE = "incomplete", _("Incomplete")

    class PossibleSign(models.TextChoices):
        CROSS = "❌", _("Cross")
        NOUGHT = "⭕", _("Nought")

    # Fields for player1 (initiator of the invitation, required)
    player1_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="player1_propositions",
        limit_choices_to=Q(app_label="user_management", model="user")
        | Q(app_label="user_management", model="tguser"),
        help_text="ContentType of the object for player 1, required (e.g. TgUser or User).",
    )
    player1_object_id = models.PositiveBigIntegerField(
        help_text="Player 1's object ID, required (e.g. TgUser.id or User.id)."
    )
    player1 = GenericForeignKey("player1_content_type", "player1_object_id")

    # Fields for player2
    # (may be null if the invitation has not yet been accepted, or a second player has not been specified)
    player2_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="player2_propositions",
        null=True,
        blank=True,
        limit_choices_to=Q(app_label="user_management", model="user")
        | Q(app_label="user_management", model="tguser"),
        help_text="ContentType of the object for player 2, optional (e.g. TgUser or User).",
    )
    player2_object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text="Player 1's object ID, optional (e.g. TgUser.id or User.id).",
    )
    player2 = GenericForeignKey("player2_content_type", "player2_object_id")

    # Determines who goes first: True - player1, False - player2, None - not defined
    player1_first = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("player1 goes first"),
        help_text="Indicates whether player 1 goes first. True - player 1, False - player 2, None - not defined.",
    )

    # Player's signs (can be null if not defined)
    player1_sign = models.CharField(
        max_length=1,
        choices=PossibleSign.choices,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("player1 sign"),
        help_text=(
            f"Player 1's sign, possible: {PossibleSign.values}. Cannot be the same for different players. "
            f"When creating an offer, can be verbal, must be set before accepting the game."
        ),
    )
    player2_sign = models.CharField(
        max_length=1,
        choices=PossibleSign.choices,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("player2 sign"),
        help_text=(
            f"Player 2's sign, possible: {PossibleSign.values}. Cannot be the same for different players. "
            f"When creating an offer, can be verbal, must be set before accepting the game."
        ),
    )

    # Date the offer was created.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
        help_text="Date the offer was created. Set automatically.",
    )

    #
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("accepted at"),
        help_text=(
            f"Time of acceptance of the offer (null, if not yet accepted). Setting the status "
            f"{PossibleStatus.ACCEPTED} is possible only for a fully completed offer and with "
            f"the accepted_at field set (the time will be adjusted at the time of setting)."
        ),
    )

    status = models.CharField(
        max_length=20,
        choices=PossibleStatus.choices,
        default="pending",
        verbose_name=_("statuses"),
        help_text=f"Offer status: {PossibleStatus.values}.",
    )

    # Offer expiration time (7 days from created_at by default)
    expires_at = models.DateTimeField(
        default=get_data_expired,
        verbose_name=_("expires at"),
        help_text="Offer expiration date (default will be set to +7 days from current time).",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text="Indicates whether the proposal is active. Changes to False during a DELETE request.",
    )

    class Meta:
        verbose_name = _("TicTacToe proposition")
        verbose_name_plural = _("TicTacToe propositions")
        indexes = [
            models.Index(fields=["player1_object_id"]),
            models.Index(fields=["player2_object_id"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["accepted_at"]),
            models.Index(fields=["expires_at"]),
        ]
        #
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "player1_content_type",
                    "player1_object_id",
                    "player2_content_type",
                    "player2_object_id",
                ],
                condition=(
                    (models.Q(status="incomplete") | models.Q(status="pending"))
                    & models.Q(player2_object_id__isnull=False)
                ),
                name="unique_pending_incomplete_proposition",
            )
        ]

    def __str__(self):
        player2_str = str(self.player2) if self.player2 else "Unknown"
        return f"Proposition {self.id}: {self.player1} vs {player2_str} ({self.status})"

    @property
    def is_expired(self):
        return self.expires_at < timezone.now() if self.expires_at else False

    def clean(self):
        """Валідація моделі."""
        # Checking that player1 is not equal to player2
        if (
            self.player2_content_type
            and self.player1_content_type == self.player2_content_type
            and self.player1_object_id == self.player2_object_id
        ):
            raise ValidationError(_("Player 1 and Player 2 cannot be the same."))

        # Checking that the players' signs are different if both are specified
        if (
            self.player1_sign
            and self.player2_sign
            and self.player1_sign == self.player2_sign
        ):
            raise ValidationError(_("Player 1 and Player 2 must have different signs."))

        # Check that the characters are correct, if specified
        valid_signs = [
            choice[0] for choice in self._meta.get_field("player1_sign").choices
        ]
        if self.player1_sign and self.player1_sign not in valid_signs:
            raise ValidationError(_("Invalid sign selected for Player 1."))
        if self.player2_sign and self.player2_sign not in valid_signs:
            raise ValidationError(_("Invalid sign selected for Player 2."))

        # Checking that expires_at is not earlier than created_at
        if self.expires_at and self.created_at and self.expires_at < self.created_at:
            raise ValidationError(
                _("Expiration date cannot be earlier than creation date.")
            )

        # Checking accepted_at and status consistency
        if (self.status == self.PossibleStatus.ACCEPTED or self.accepted_at) and (
            not self.player2
            or not self.player2_sign
            or not self.player1_sign
            or self.player1_first is None
            or self.status != self.PossibleStatus.ACCEPTED
            or not self.accepted_at
        ):
            raise ValidationError(
                _(
                    f"{self.PossibleStatus.ACCEPTED} status and set the field 'accepted_at' requires to fill out all fields for Game."
                )
            )

        # Setting "accepted_at" requires setting the status to "accepted"
        if (
            self.status in [self.PossibleStatus.PENDING, self.PossibleStatus.INCOMPLETE]
            and self.accepted_at
        ):
            raise ValidationError(
                _(
                    f"{self.PossibleStatus.PENDING} or {self.PossibleStatus.INCOMPLETE} status cannot have accepted_at set."
                )
            )

        # If the status is DECLINED, accepted_at should not be set
        if self.status == self.PossibleStatus.DECLINED and self.accepted_at:
            raise ValidationError(
                _(f"{self.PossibleStatus.DECLINED} status cannot have accepted_at set.")
            )

    def save(self, *args, **kwargs):
        """
        Automatically set the status to 'incomplete' if the offer has empty fields, when setting the status
        to "accepted" and not setting the accepted_at field - automatically sets it to the current time (and
        vice versa - setting the accepted_at field without setting the status - automatically sets the
        status to "accepted").
        """
        if (
            self.player2 is None
            or self.player1_first is None
            or self.player1_sign is None
            or self.player2_sign is None
        ) and self.status != self.PossibleStatus.DECLINED:
            self.status = self.PossibleStatus.INCOMPLETE
        elif self.status == self.PossibleStatus.ACCEPTED and not self.accepted_at:
            self.accepted_at = timezone.now()
        elif self.accepted_at and self.status != self.PossibleStatus.ACCEPTED:
            self.accepted_at = timezone.now()
            self.status = self.PossibleStatus.ACCEPTED
        self.full_clean()
        super().save(*args, **kwargs)


class Game(models.Model):
    player1_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="player1_games",
        limit_choices_to={
            "model__in": ("user_management.user", "user_management.tguser")
        },
    )
    player1_object_id = models.PositiveIntegerField()
    player1 = GenericForeignKey("player1_content_type", "player1_object_id")

    # Поля для player2 (другий гравець)
    player2_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="player2_games",
        limit_choices_to={
            "model__in": ("user_management.user", "user_management.tguser")
        },
    )
    player2_object_id = models.PositiveIntegerField()
    player2 = GenericForeignKey("player2_content_type", "player2_object_id")
    player1_symbol = models.CharField(
        max_length=1,
        choices=[("❌", "Cross"), ("⭕", "Nought")],
        verbose_name=_("player 1 symbol"),
    )
    player2_symbol = models.CharField(
        max_length=1,
        choices=[("❌", "Cross"), ("⭕", "Nought")],
        verbose_name=_("player 2 symbol"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("game")
        verbose_name_plural = _("games")
        indexes = [
            models.Index(fields=["player1_object_id"]),
            models.Index(fields=["player2_object_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Game {self.id}: {self.player1} ({self.player1_symbol}) vs {self.player2} ({self.player2_symbol})"

    def clean(self):
        """Валідація моделі"""
        # Перевірка, що гравці різні
        if (
            self.player1_content_type == self.player2_content_type
            and self.player1_object_id == self.player2_object_id
        ):
            raise ValidationError(_("Player 1 and Player 2 cannot be the same."))

        # Перевірка, що символи гравців різні
        if self.player1_symbol == self.player2_symbol:
            raise ValidationError(
                _("Player 1 and Player 2 must have different symbols.")
            )

        # Перевірка, що символи є коректними Unicode-символами для гри
        valid_symbols = [
            choice[0] for choice in self._meta.get_field("player1_symbol").choices
        ]
        if (
            self.player1_symbol not in valid_symbols
            or self.player2_symbol not in valid_symbols
        ):
            raise ValidationError(_("Invalid symbol selected for player."))


class GameState(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_state")
    cells = models.CharField(
        max_length=9,
        default=" " * 9,
        validators=[
            RegexValidator(
                regex=r"^[\sX0]{9}$",
                message=_("Must contain 9 cells of: X, 0(null), or space"),
            )
        ],
    )
    parent_state = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="child_state",
    )
    created_at = models.DateTimeField(auto_now_add=True)
