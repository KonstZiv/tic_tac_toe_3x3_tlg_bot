from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.username} ({self.email})" if self.username else self.email


class TgUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tlg_user", null=True)
    tg_id = models.BigIntegerField(unique=True)
    tg_first_name = models.CharField(max_length=255)
    tg_last_name = models.CharField(max_length=255, blank=True, null=True)
    tg_username = models.CharField(max_length=255, blank=True, null=True)
    is_bot = models.BooleanField(default=False)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    added_to_attachment_menu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"username: {self.tg_username}" if self.tg_username else
            f"first_name: {self.tg_first_name}"
            + f" ({self.tg_id})"
        )
