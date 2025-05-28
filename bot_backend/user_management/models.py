from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction, DatabaseError
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields['is_staff'] = False
        extra_fields['is_superuser'] = False
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(
        verbose_name=_("username"),
        max_length=150,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        verbose_name=_("email address"),
        unique=True,
        db_index=True,
    )

    player1_games = GenericRelation(
        'tictactoe.Game',
        content_type_field='player1_content_type',
        object_id_field='player1_object_id',
        related_query_name='user_player1_games'
    )

    player2_games = GenericRelation(
        'tictactoe.Game',
        content_type_field='player2_content_type',
        object_id_field='player2_object_id',
        related_query_name='user_player2_games'
    )

    player1_propositions = GenericRelation(
        'tictactoe.TicTacToeProposition',
        content_type_field='player1_content_type',
        object_id_field='player1_object_id',
        related_query_name='user_player1_propositions'
    )
    player2_propositions = GenericRelation(
        'tictactoe.TicTacToeProposition',
        content_type_field='player2_content_type',
        object_id_field='player2_object_id',
        related_query_name='user_player2_propositions'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.username} ({self.email})" if self.username else self.email

    @property
    def games(self):
        """Об’єднує ігри, де користувач є player1 або player2"""
        return self.player1_games.all() | self.player2_games.all()


class TgUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tlg_user", null=True)
    tg_id = models.BigIntegerField(unique=True)
    tg_first_name = models.CharField(max_length=255)
    tg_last_name = models.CharField(max_length=255, blank=True, null=True)
    tg_username = models.CharField(max_length=255, blank=True, null=True)
    is_bot = models.BooleanField(default=False)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    is_premium = models.BooleanField(default=False, null=True)
    added_to_attachment_menu = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Зворотні зв’язки для ігор, де TgUser є player1
    player1_games = GenericRelation(
        'tictactoe.Game',
        content_type_field='player1_content_type',
        object_id_field='player1_object_id',
        related_query_name='tguser_player1_games'
    )

    # Зворотні зв’язки для ігор, де TgUser є player2
    player2_games = GenericRelation(
        'tictactoe.Game',
        content_type_field='player2_content_type',
        object_id_field='player2_object_id',
        related_query_name='tguser_player2_games'
    )

    player1_propositions = GenericRelation(
        'tictactoe.TicTacToeProposition',
        content_type_field='player1_content_type',
        object_id_field='player1_object_id',
        related_query_name='tguser_player1_propositions'
    )
    player2_propositions = GenericRelation(
        'tictactoe.TicTacToeProposition',
        content_type_field='player2_content_type',
        object_id_field='player2_object_id',
        related_query_name='tguser_player2_propositions'
    )

    @property
    def games(self):
        """Об’єднує ігри, де TgUser є player1 або player2"""
        return self.player1_games.all() | self.player2_games.all()

    def __str__(self):
        return (
            f"username: {self.tg_username}" if self.tg_username else
            f"first_name: {self.tg_first_name}"
            + f" ({self.tg_id})"
        )

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
                tguser = super().save(*args, **kwargs)
                attempt = TgStartAttempt.objects.create(tg_user=self)
                attempt.save()
                return tguser
        except DatabaseError as e:
            # Обробка помилки, якщо потрібно
            print(f"Error saving TgUser with new TgStartAttempt: {e}")
            raise


class TgStartAttempt(models.Model):
    tg_user = models.ForeignKey(TgUser, on_delete=models.CASCADE, related_name="start_attempts")
    attempt_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Tg Start Attempt")
        verbose_name_plural = _("Tg Start Attempts")
        ordering = ["-attempt_time"]

    def __str__(self):
        return f"Attempt 'start/' by {self.tg_user} at {self.attempt_time}"
