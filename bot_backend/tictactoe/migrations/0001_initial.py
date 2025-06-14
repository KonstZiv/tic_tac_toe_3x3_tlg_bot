# Generated by Django 5.2.1 on 2025-06-04 14:12

import django.core.validators
import django.db.models.deletion
import tictactoe.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("player1_object_id", models.PositiveIntegerField()),
                ("player2_object_id", models.PositiveIntegerField()),
                (
                    "player1_symbol",
                    models.CharField(
                        choices=[("❌", "Cross"), ("⭕", "Nought")],
                        max_length=1,
                        verbose_name="player 1 symbol",
                    ),
                ),
                (
                    "player2_symbol",
                    models.CharField(
                        choices=[("❌", "Cross"), ("⭕", "Nought")],
                        max_length=1,
                        verbose_name="player 2 symbol",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "player1_content_type",
                    models.ForeignKey(
                        limit_choices_to={
                            "model__in": (
                                "user_management.user",
                                "user_management.tguser",
                            )
                        },
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="player1_games",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "player2_content_type",
                    models.ForeignKey(
                        limit_choices_to={
                            "model__in": (
                                "user_management.user",
                                "user_management.tguser",
                            )
                        },
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="player2_games",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "game",
                "verbose_name_plural": "games",
            },
        ),
        migrations.CreateModel(
            name="GameState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cells",
                    models.CharField(
                        default="         ",
                        max_length=9,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Must contain 9 cells of: X, 0(null), or space",
                                regex="^[\\sX0]{9}$",
                            )
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="game_state",
                        to="tictactoe.game",
                    ),
                ),
                (
                    "parent_state",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="child_state",
                        to="tictactoe.gamestate",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TicTacToeProposition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("player1_object_id", models.PositiveIntegerField()),
                (
                    "player2_object_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "player1_first",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="player1 goes first",
                    ),
                ),
                (
                    "player1_sign",
                    models.CharField(
                        blank=True,
                        choices=[("❌", "Cross"), ("⭕", "Nought")],
                        default=None,
                        max_length=1,
                        null=True,
                        verbose_name="player1 sign",
                    ),
                ),
                (
                    "player2_sign",
                    models.CharField(
                        blank=True,
                        choices=[("❌", "Cross"), ("⭕", "Nought")],
                        default=None,
                        max_length=1,
                        null=True,
                        verbose_name="player2 sign",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "accepted_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="accepted at"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("rejected", "Rejected"),
                            ("incomplete", "Incomplete"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "expires_at",
                    models.DateTimeField(
                        default=tictactoe.models.get_data_expired,
                        help_text="The date and time when the proposition expires (default: 7 days from creation).",
                        verbose_name="expires at",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="is active"),
                ),
                (
                    "player1_content_type",
                    models.ForeignKey(
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "user_management"), ("model", "user")
                            ),
                            models.Q(
                                ("app_label", "user_management"), ("model", "tguser")
                            ),
                            _connector="OR",
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="player1_propositions",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "player2_content_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "user_management"), ("model", "user")
                            ),
                            models.Q(
                                ("app_label", "user_management"), ("model", "tguser")
                            ),
                            _connector="OR",
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="player2_propositions",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "TicTacToe proposition",
                "verbose_name_plural": "TicTacToe propositions",
            },
        ),
        migrations.AddIndex(
            model_name="game",
            index=models.Index(
                fields=["player1_object_id"], name="tictactoe_g_player1_cf9796_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="game",
            index=models.Index(
                fields=["player2_object_id"], name="tictactoe_g_player2_4f15c9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="game",
            index=models.Index(
                fields=["created_at"], name="tictactoe_g_created_bcc041_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tictactoeproposition",
            index=models.Index(
                fields=["player1_object_id"], name="tictactoe_t_player1_bd388a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tictactoeproposition",
            index=models.Index(
                fields=["player2_object_id"], name="tictactoe_t_player2_1bb2cb_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tictactoeproposition",
            index=models.Index(
                fields=["created_at"], name="tictactoe_t_created_1f43c8_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tictactoeproposition",
            index=models.Index(
                fields=["accepted_at"], name="tictactoe_t_accepte_ffc257_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tictactoeproposition",
            index=models.Index(
                fields=["expires_at"], name="tictactoe_t_expires_c411d4_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="tictactoeproposition",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "pending")),
                fields=(
                    "player1_content_type",
                    "player1_object_id",
                    "player2_content_type",
                    "player2_object_id",
                ),
                name="unique_pending_proposition",
            ),
        ),
    ]
