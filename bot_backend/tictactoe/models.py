from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db import models

from user_management.models import TgUser, User


class Game(models.Model):
    player1_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='player1_games',
        limit_choices_to={'model__in': ('user_management.user', 'user_management.tguser')},
    )
    player1_object_id = models.PositiveIntegerField()
    player1 = GenericForeignKey('player1_content_type', 'player1_object_id')

    # Поля для player2 (другий гравець)
    player2_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='player2_games',
        limit_choices_to={'model__in': ('user_management.user', 'user_management.tguser')},
    )
    player2_object_id = models.PositiveIntegerField()
    player2 = GenericForeignKey('player2_content_type', 'player2_object_id')
    player1_symbol = models.CharField(
        max_length=1,
        choices=[('❌', 'Cross'), ('⭕', 'Nought')],
        verbose_name=_("player 1 symbol"),
    )
    player2_symbol = models.CharField(
        max_length=1,
        choices=[('❌', 'Cross'), ('⭕', 'Nought')],
        verbose_name=_("player 2 symbol"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("game")
        verbose_name_plural = _("games")
        indexes = [
            models.Index(fields=['player1_object_id']),
            models.Index(fields=['player2_object_id']),
            models.Index(fields=['created_at']),
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
            raise ValidationError(_("Player 1 and Player 2 must have different symbols."))

        # Перевірка, що символи є коректними Unicode-символами для гри
        valid_symbols = [choice[0] for choice in self._meta.get_field('player1_symbol').choices]
        if self.player1_symbol not in valid_symbols or self.player2_symbol not in valid_symbols:
            raise ValidationError(_("Invalid symbol selected for player."))


class GameState(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_state')
    cells = models.CharField(
        max_length=9,
        default=" " * 9,
        validators=[RegexValidator(regex=r"^[\sX0]{9}$", message=_("Must contain 9 cells of: X, 0(null), or space"))]
    )
    parent_state = models.OneToOneField("self", null=True, blank=True, on_delete=models.CASCADE, related_name='child_state')
    created_at = models.DateTimeField(auto_now_add=True)
