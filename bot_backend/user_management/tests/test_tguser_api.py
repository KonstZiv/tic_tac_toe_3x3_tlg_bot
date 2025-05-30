import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from user_management.models import TgUser, TgStartAttempt


@pytest.fixture
def api_client():
    """Фікстура для API-клієнта."""
    return APIClient()


@pytest.fixture
def tg_user():
    """Фікстура для створення TgUser."""
    return TgUser.objects.create(
        tg_id=123456789,
        tg_first_name='John',
        tg_last_name='Doe',
        tg_username='@JohnDoe',
        is_bot=False,
        language_code='en',
        is_premium=False,
        added_to_attachment_menu=False
    )


@pytest.mark.django_db
class TestTgUserAPI:
    def test_get_method_not_allowed(self, api_client):
        """Перевіряє, що GET повертає 405 Method Not Allowed."""
        url = reverse('user_management:tgusers-list')
        response = api_client.get(url)
        assert response.status_code == 405
        assert response.data['detail'] == 'Method "GET" not allowed.'

    def test_post_creates_new_user_and_start_attempt(self, api_client):
        """Перевіряє створення нового TgUser та TgStartAttempt."""
        url = reverse('user_management:tgusers-list')
        data = {
            'tg_id': 123456789,
            'tg_first_name': 'John',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnDoe',
            'is_bot': False,
            'language_code': 'en',
            'is_premium': False,
            'added_to_attachment_menu': False
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201
        assert TgUser.objects.count() == 1
        assert TgStartAttempt.objects.count() == 1
        user = TgUser.objects.get(tg_id=123456789)
        assert user.tg_first_name == 'John'
        assert user.tg_last_name == 'Doe'
        assert user.tg_username == '@JohnDoe'
        assert TgStartAttempt.objects.filter(tg_user=user).exists()

    def test_post_updates_user_and_creates_start_attempt(self, api_client, tg_user):
        """Перевіряє оновлення TgUser та створення TgStartAttempt."""
        url = reverse('user_management:tgusers-list')
        data = {
            'tg_id': 123456789,
            'tg_first_name': 'Johnny',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnnyDoe',
            'is_bot': False,
            'language_code': 'uk',
            'is_premium': True,
            'added_to_attachment_menu': False
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201
        tg_user.refresh_from_db()
        assert tg_user.tg_first_name == 'Johnny'
        assert tg_user.language_code == 'uk'
        assert tg_user.is_premium is True
        assert TgUser.objects.count() == 1
        assert TgStartAttempt.objects.count() == 1
        assert TgStartAttempt.objects.filter(tg_user=tg_user).exists()

    def test_post_no_user_update_but_creates_start_attempt(self, api_client, tg_user):
        """Перевіряє, що TgUser не оновлюється, але TgStartAttempt створюється."""
        url = reverse('user_management:tgusers-list')
        original_updated_at = tg_user.updated_at
        data = {
            'tg_id': 123456789,
            'tg_first_name': 'John',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnDoe',
            'is_bot': False,
            'language_code': 'en',
            'is_premium': False,
            'added_to_attachment_menu': False
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201
        tg_user.refresh_from_db()
        assert tg_user.updated_at == original_updated_at
        assert TgUser.objects.count() == 1
        assert TgStartAttempt.objects.count() == 1
        assert TgStartAttempt.objects.filter(tg_user=tg_user).exists()

    def test_post_invalid_data(self, api_client):
        """Перевіряє обробку невалідних даних (від’ємний tg_id)."""
        url = reverse('user_management:tgusers-list')
        data = {
            'tg_id': -123456789,
            'tg_first_name': 'John',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnDoe',
            'is_bot': False,
            'language_code': 'en'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
        assert 'tg_id' in response.data
        assert TgUser.objects.count() == 0
        assert TgStartAttempt.objects.count() == 0
