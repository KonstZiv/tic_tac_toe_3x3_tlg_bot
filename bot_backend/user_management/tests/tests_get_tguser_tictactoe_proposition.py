from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from tictactoe.models import TicTacToeProposition
from user_management.models import TgUser, User


class TicTacToePropositionViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tguser = TgUser.objects.create(id=123456789, tg_first_name='John')
        self.content_type_tg = ContentType.objects.get_for_model(TgUser)
        self.user = User.objects.create_user(email="user@user.user", username="TestWebUser")
        self.content_type_user = ContentType.objects.get_for_model(User)
        self.proposition = TicTacToeProposition.objects.create(
            player1_content_type=self.content_type_tg,
            player1_object_id=self.tguser.id,
            status='incomplete',
            expires_at=timezone.now() + timedelta(days=7)
        )
        self.proposition2 = TicTacToeProposition.objects.create(
            player1_content_type=self.content_type_user,
            player1_object_id=self.user.id,
            player2_content_type=self.content_type_tg,
            player2_object_id=self.tguser.id,
            created_at=timezone.now() - timedelta(seconds=1),
            expires_at=timezone.now(),
        )

    def tearDown(self):
        TicTacToeProposition.objects.all().delete()
        User.objects.all().delete()
        TgUser.objects.all().delete()

    def test_simply_request(self):
        url = reverse('api_user_management:tguser-tictactoe-propositions-list', kwargs={'tguser_pk': self.tguser.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_filter_by_status(self):
        url = reverse('api_user_management:tguser-tictactoe-propositions-list', kwargs={'tguser_pk': self.tguser.id})
        response = self.client.get(url, {'statuses': 'incomplete'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]['status'], 'incomplete')
        response2 = self.client.get(url, {'statuses': 'accepted'})
        self.assertEqual(len(response2.data["results"]), 0)

    def test_filter_by_is_player1(self):
        url = reverse('api_user_management:tguser-tictactoe-propositions-list', kwargs={'tguser_pk': self.tguser.id})
        response = self.client.get(url, {'is_player1': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]['player1']["id"], self.tguser.id)
