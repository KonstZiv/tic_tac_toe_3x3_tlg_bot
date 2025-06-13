from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from tictactoe.models import TicTacToeProposition
from user_management.models import User, TgUser


class TicTacToePropositionTestCase(TestCase):
    def setUp(self):
        # Create a TicTacToeProposition instance for testing
        self.user = User.objects.create_user(
            email="user@user.user", password="password"
        )
        self.tg_user = TgUser.objects.create(id=123456789, tg_username="tguser")
        self.user_content_type = self.user.get_content_type()
        self.tg_user_content_type = self.tg_user.get_content_type()

    def tearDown(self):
        # Clean up after each test
        TicTacToeProposition.objects.all().delete()
        User.objects.all().delete()
        TgUser.objects.all().delete()

    def test_proposition_creation_with_minimum_data(self):
        """Test that the proposition is created correctly.
        one user
        two users
        check all fields
        """
        # one user
        proposition1 = TicTacToeProposition.objects.create(
            player1_content_type=self.user.get_content_type(),
            player1_object_id=self.user.id,
        )
        self.assertEqual(proposition1.player1, self.user)
        self.assertIsNone(proposition1.player2)
        self.assertEqual(proposition1.status, "incomplete")
        self.assertIsNone(proposition1.accepted_at)
        self.assertGreaterEqual(
            (proposition1.expires_at - proposition1.created_at).days, 6
        )
        self.assertIsNone(proposition1.player1_first)
        self.assertIsNone(proposition1.player1_sign)
        self.assertIsNone(proposition1.player2_sign)

    def test_proposition_creation_with_two_users_and_all_fields(self):
        """Test that the proposition is created correctly with two users."""
        # two users
        proposition2 = TicTacToeProposition.objects.create(
            player1_content_type=self.user.get_content_type(),
            player1_object_id=self.user.id,
            player2_content_type=self.tg_user.get_content_type(),
            player2_object_id=self.tg_user.id,
            player1_first=True,
            player1_sign=TicTacToeProposition.PossibleSign.CROSS,
            player2_sign=TicTacToeProposition.PossibleSign.NOUGHT,
        )
        self.assertEqual(proposition2.player1, self.user)
        self.assertEqual(proposition2.player2, self.tg_user)
        self.assertEqual(
            proposition2.status, TicTacToeProposition.PossibleStatus.PENDING
        )
        self.assertIsNone(proposition2.accepted_at)
        self.assertGreaterEqual(
            (proposition2.expires_at - proposition2.created_at).days, 6
        )
        self.assertTrue(proposition2.player1_first)
        self.assertEqual(
            proposition2.player1_sign, TicTacToeProposition.PossibleSign.CROSS
        )
        self.assertEqual(
            proposition2.player2_sign, TicTacToeProposition.PossibleSign.NOUGHT
        )

    def test_proposition_creation_with_two_users_without_all_fields(self):
        """Test that the proposition is created correctly with two users."""
        # two users
        proposition3 = TicTacToeProposition.objects.create(
            player1_content_type=self.user.get_content_type(),
            player1_object_id=self.user.id,
            player2_content_type=self.tg_user.get_content_type(),
            player2_object_id=self.tg_user.id,
            player1_sign=TicTacToeProposition.PossibleSign.CROSS,
            player2_sign=TicTacToeProposition.PossibleSign.NOUGHT,
        )
        self.assertEqual(proposition3.player1, self.user)
        self.assertEqual(proposition3.player2, self.tg_user)
        self.assertEqual(
            proposition3.status, TicTacToeProposition.PossibleStatus.INCOMPLETE
        )
        self.assertIsNone(proposition3.accepted_at)
        self.assertGreaterEqual(
            (proposition3.expires_at - proposition3.created_at).days, 6
        )
        self.assertIsNone(proposition3.player1_first)
        self.assertEqual(
            proposition3.player1_sign, TicTacToeProposition.PossibleSign.CROSS
        )
        self.assertEqual(
            proposition3.player2_sign, TicTacToeProposition.PossibleSign.NOUGHT
        )

    def test_validation_player1_not_the_same_as_player2(self):
        """Test that the proposition is not created if player1 and player2 are the same."""
        with self.assertRaises(ValidationError):
            proposition = TicTacToeProposition.objects.create(
                player1_content_type=self.user.get_content_type(),
                player1_object_id=self.user.id,
                player2_content_type=self.user.get_content_type(),
                player2_object_id=self.user.id,
            )

    def test_validation_expired_at_not_less_than_created_at(self):
        """Test that the proposition is not created if expires_at is less than created_at."""
        with self.assertRaises(ValidationError):
            proposition = TicTacToeProposition.objects.create(
                player1_content_type=self.user.get_content_type(),
                player1_object_id=self.user.id,
            )
            proposition.expires_at = proposition.created_at - timedelta(days=1)
            proposition.save()

    def test_validation_player1_sign_and_player2_sign_not_the_same(self):
        """Test that the proposition is not created if player1_sign and player2_sign are the same."""
        with self.assertRaises(ValidationError):
            proposition = TicTacToeProposition.objects.create(
                player1_content_type=self.user.get_content_type(),
                player1_object_id=self.user.id,
                player2_content_type=self.tg_user.get_content_type(),
                player2_object_id=self.tg_user.id,
                player1_sign=TicTacToeProposition.PossibleSign.CROSS,
                player2_sign=TicTacToeProposition.PossibleSign.CROSS,
            )

    def test_validation_sign_is_possible_symbol(self):
        """Test that the proposition is not created if player1_sign or player2_sign is not a possible symbol."""
        with self.assertRaises(ValidationError):
            proposition = TicTacToeProposition.objects.create(
                player1_content_type=self.user.get_content_type(),
                player1_object_id=self.user.id,
                player2_content_type=self.tg_user.get_content_type(),
                player2_object_id=self.tg_user.id,
                player1_sign="X",  # Invalid sign
                player2_sign=TicTacToeProposition.PossibleSign.NOUGHT,
            )

    def test_unset_accepted_status_with_incomplete_data(self):
        """Test that the proposition is not set to accepted if it is incomplete."""

        proposition = TicTacToeProposition.objects.create(
            player1_content_type=self.user.get_content_type(),
            player1_object_id=self.user.id,
            status=TicTacToeProposition.PossibleStatus.INCOMPLETE,
        )
        self.assertEqual(
            proposition.status, TicTacToeProposition.PossibleStatus.INCOMPLETE
        )
