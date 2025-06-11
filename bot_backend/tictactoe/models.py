from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def get_data_expired(timestamp=None, period: timedelta = timedelta(days=7)):
    """Функція для отримання дати закінчення терміну дії пропозиції (7 днів від створення)."""
    if timestamp is None:
        timestamp = timezone.now()
    return timestamp + period


class PossibleSign(models.TextChoices):
    CROSS = '❌', _('Cross')
    NOUGHT = '⭕', _('Nought')


class TicTacToeProposition(models.Model):
    """
    Модель пропозиції гри в хрестики-нулики для користувачів Telegram.
    Зберігає інформацію про гравців, налаштування гри та статус пропозиції.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('incomplete', 'Incomplete'),
        ('completed', 'Completed'),
    )

    # Поля для player1 (ініціатор запрошення, обов’язкове)
    player1_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='player1_propositions',
        limit_choices_to=Q(app_label='user_management', model='user') | Q(app_label='user_management', model='tguser'),
        help_text='ContentType об’єкта для гравця 1 (наприклад, TgUser).'
    )
    player1_object_id = models.PositiveBigIntegerField(
        help_text='ID об’єкта гравця 1 (наприклад, Telegram ID).'
    )
    player1 = GenericForeignKey('player1_content_type', 'player1_object_id')

    # Поля для player2 (може бути null, якщо запрошення ще не прийнято)
    player2_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='player2_propositions',
        null=True,
        blank=True,
        limit_choices_to=Q(app_label='user_management', model='user') | Q(app_label='user_management', model='tguser'),
        help_text='ContentType для гравця 2 (може бути null).',
    )
    player2_object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text='ID об’єкта гравця 2 (може бути null).',
    )
    player2 = GenericForeignKey('player2_content_type', 'player2_object_id')

    # Визначає, хто ходить першим: True - player1, False - player2, None - не визначено
    player1_first = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("player1 goes first"),
        help_text='Вказує, чи ходить гравець 1 першим.',
    )

    # Знаки гравців (можуть бути null, якщо не визначено)
    player1_sign = models.CharField(
        max_length=1,
        choices=PossibleSign.choices,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("player1 sign"),
        help_text='Знак гравця 1 (наприклад, "❌" або "⭕").'
    )
    player2_sign = models.CharField(
        max_length=1,
        choices=PossibleSign.choices,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("player2 sign"),
        help_text='Знак гравця 2 (наприклад, "❌" або "⭕").'
    )

    # Час створення пропозиції
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
        help_text='Дата створення пропозиції.',
    )

    # Час прийняття пропозиції (null, якщо ще не прийнято)
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("accepted at"),
        help_text='Дата прийняття пропозиції (може бути null).',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("statuses"),
        help_text='Статус пропозиції (pending, accepted, declined, incomplete, completed).',
    )

    # Час закінчення терміну дії пропозиції (7 днів від created_at за замовчуванням)
    expires_at = models.DateTimeField(
        default=get_data_expired,
        verbose_name=_("expires at"),
        help_text='Дата закінчення терміну дії пропозиції (може бути null - буде встановлено +7 днів від поточної).'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text='Вказує, чи є пропозиція активною.',
    )

    class Meta:
        verbose_name = _("TicTacToe proposition")
        verbose_name_plural = _("TicTacToe propositions")
        indexes = [
            models.Index(fields=['player1_object_id']),
            models.Index(fields=['player2_object_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['accepted_at']),
            models.Index(fields=['expires_at']),
        ]
        # Унікальність пропозиції: не можна створити дві однакові пропозиції з однаковими player1 і player2, якщо статус "pending"
        constraints = [
            models.UniqueConstraint(
                fields=['player1_content_type', 'player1_object_id', 'player2_content_type', 'player2_object_id'],
                condition=models.Q(status='pending'),
                name='unique_pending_proposition'
            )
        ]

    def __str__(self):
        player2_str = str(self.player2) if self.player2 else "Not accepted"
        status = "Accepted" if self.accepted_at else "Pending"
        return f"Proposition {self.id}: {self.player1} vs {player2_str} ({status})"

    @property
    def is_expired(self):
        return self.expires_at < timezone.now() if self.expires_at else False

    def clean(self):
        """Валідація моделі."""
        # Перевірка, що player1 не дорівнює player2
        if (
                self.player2_content_type
                and self.player1_content_type == self.player2_content_type
                and self.player1_object_id == self.player2_object_id
        ):
            raise ValidationError(_("Player 1 and Player 2 cannot be the same."))

        # Перевірка, що знаки гравців різні, якщо обидва вказані
        if self.player1_sign and self.player2_sign and self.player1_sign == self.player2_sign:
            raise ValidationError(_("Player 1 and Player 2 must have different signs."))

        # Перевірка, що знаки коректні, якщо вказані
        valid_signs = [choice[0] for choice in self._meta.get_field('player1_sign').choices]
        if self.player1_sign and self.player1_sign not in valid_signs:
            raise ValidationError(_("Invalid sign selected for Player 1."))
        if self.player2_sign and self.player2_sign not in valid_signs:
            raise ValidationError(_("Invalid sign selected for Player 2."))

        # Перевірка, що accepted_at встановлено лише якщо є player2
        if self.accepted_at and not self.player2:
            raise ValidationError(_("Accepted timestamp cannot be set without Player 2."))

        # Перевірка, що expires_at не раніше created_at
        if self.expires_at and self.created_at and self.expires_at < self.created_at:
            raise ValidationError(_("Expiration date cannot be earlier than creation date."))

        # Валідація status
        if self.status == 'accepted' and (
                not self.player2 or
                not self.player2_sign or
                not self.player1_sign or
                self.player1_first is None
        ):
            raise ValidationError(_("Accepted status requires Player 2 and accepted_at to be set."))
        if self.status in ['pending', 'incomplete'] and self.accepted_at:
            raise ValidationError(_("Pending or incomplete status cannot have accepted_at set."))
        if self.status == 'rejected' and self.accepted_at:
            raise ValidationError(_("Rejected status cannot have accepted_at set."))

    def save(self, *args, **kwargs):
        """Автоматична валідація перед збереженням та встановлення статусу 'incomplete' якщо пропозиція має незаповнені поля."""
        if self.player2 is None or self.player1_first is None or self.player1_sign is None or self.player2_sign is None:
            self.status = 'incomplete'
        elif self.status == 'accepted' and not self.accepted_at:
            self.accepted_at = timezone.now()
        self.full_clean()
        super().save(*args, **kwargs)


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
    parent_state = models.OneToOneField("self", null=True, blank=True, on_delete=models.CASCADE,
                                        related_name='child_state')
    created_at = models.DateTimeField(auto_now_add=True)
