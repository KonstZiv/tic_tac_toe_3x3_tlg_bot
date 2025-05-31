import os
from pathlib import Path

import pytest
from decouple import Config, RepositoryEnv
from django.db import DatabaseError
from django.urls import reverse
from rest_framework.test import APIClient

from user_management.models import TgUser, TgStartAttempt


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Завантажує змінні оточення з .env.local."""
    env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env.local'
    env = RepositoryEnv(env_path)
    for key, value in env.data.items():
        os.environ[key] = str(value)


@pytest.fixture
def api_client():
    """Фікстура для API-клієнта."""
    return APIClient()


@pytest.fixture
def tg_user():
    """Фікстура для створення TgUser."""
    return TgUser.objects.create(
        id=123456789,
        tg_first_name='John',
        tg_last_name='Doe',
        tg_username='@JohnDoe',
        is_bot=False,
        language_code='en',
        is_premium=False,
        added_to_attachment_menu=None
    )


@pytest.mark.django_db
class TestTgUserAPI:
    def test_get_method_not_allowed(self, api_client):
        """Перевіряє, що GET повертає 405 Method Not Allowed."""
        from django.conf import settings
        print(f"Current settings DB: {settings.DATABASES['default']['NAME']}")
        url = reverse('user_management/user_management:api_user_management/tgusers-list')
        response = api_client.get(url)
        assert response.status_code == 405
        assert response.data['detail'] == 'Method "GET" not allowed.'

    def test_post_creates_new_user_and_start_attempt(self, api_client):
        """Перевіряє створення нового TgUser та TgStartAttempt."""
        url = reverse('user_management/user_management:api_user_management/tgusers-list')
        data = {
            'id': 123456789,
            'tg_first_name': 'John',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnDoe',
            'is_bot': False,
            'language_code': 'en',
            'is_premium': False,
            'added_to_attachment_menu': None
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201
        assert TgUser.objects.count() == 1
        assert TgStartAttempt.objects.count() == 1
        user = TgUser.objects.get(id=123456789)
        assert user.tg_first_name == 'John'
        assert user.tg_last_name == 'Doe'
        assert user.tg_username == '@JohnDoe'
        assert TgStartAttempt.objects.filter(tg_user=user).exists()

    def test_post_updates_user_and_creates_start_attempt(self, api_client, tg_user):
        """Перевіряє оновлення TgUser та створення TgStartAttempt."""
        url = reverse('user_management/user_management:api_user_management/tgusers-list')
        data = {
            'id': 123456789,
            'tg_first_name': 'Johnny',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnnyDoe',
            'is_bot': False,
            'language_code': 'uk',
            'is_premium': True,
            'added_to_attachment_menu': None
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
        """Перевіряє, що TgUser не оновлюється, але створює TgStartAttempt."""
        url = reverse('user_management/user_management:api_user_management/tgusers-list')
        original_updated_at = tg_user.updated_at
        data = {
            'id': 123456789,
            'tg_first_name': 'John',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnDoe',
            'is_bot': False,
            'language_code': 'en',
            'is_premium': False,
            'added_to_attachment_menu': None
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201
        tg_user.refresh_from_db()
        assert tg_user.updated_at == original_updated_at
        assert TgUser.objects.count() == 1
        assert TgStartAttempt.objects.count() == 1
        assert TgStartAttempt.objects.filter(tg_user=tg_user).exists()

    def test_post_invalid_data_negative_id(self, api_client):
        """Перевіряє обробку невалідних даних (від’ємний id)."""
        url = reverse('user_management/user_management:api_user_management/tgusers-list')
        data = {
            'id': -123456789,
            'tg_first_name': 'John',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnDoe',
            'is_bot': False,
            'language_code': 'en'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
        assert 'id' in response.data
        assert TgUser.objects.count() == 0
        assert TgStartAttempt.objects.count() == 0

    def test_post_missing_required_field(self, api_client):
        """Перевіряє обробку відсутнього обов’язкового поля (tg_first_name)."""
        url = reverse('user_management/user_management:api_user_management/tgusers-list')
        data = {
            'id': 123456789,
            'tg_last_name': 'Doe',
            'tg_username': '@JohnDoe',
            'is_bot': False,
            'language_code': 'en'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
        assert 'tg_first_name' in response.data
        assert TgUser.objects.count() == 0
        assert TgStartAttempt.objects.count() == 0

    def test_post_transaction_failure(self, api_client, mocker):
        """Перевіряє атомарність транзакції при створенні TgUser і TgStartAttempt."""
        url = reverse('user_management/user_management:api_user_management/tgusers-list')
        data = {
            'id': 123456789,
            'tg_first_name': 'John',
            'tg_last_name': 'Doe',
            'tg_username': '@JohnDoe',
            'is_bot': False,
            'language_code': 'en'
        }
        # Мокуємо помилку при збереженні TgStartAttempt
        mocker.patch('user_management.models.TgStartAttempt.save', side_effect=DatabaseError)
        with pytest.raises(DatabaseError):
            api_client.post(url, data, format='json')
        assert TgUser.objects.count() == 0
        assert TgStartAttempt.objects.count() == 0
