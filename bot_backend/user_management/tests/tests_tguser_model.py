from django.test import TestCase

from user_management.models import TgUser


class TgUserModelTestCase(TestCase):
    def setUp(self):
        self.tg_user1 = TgUser.objects.create(
            id=123456789,
            tg_username="test-tguser1",
            tg_first_name="Test TgUser1",
            tg_last_name="TgUser1"
        )
        self.tg_user2 = TgUser.objects.create(
            id=987654321,
            tg_username="test-tguser2",
            tg_first_name="Test TgUser2",
            tg_last_name="TgUser2",
            language_code="en",
            is_bot=True,
        )

    def tearDown(self):
        self.tg_user1.delete()
        self.tg_user2.delete()

    def test_tg_user_creation(self):
        """Перевірка створення TgUser з обов'язковими полями."""
        self.assertEqual(self.tg_user1.id, 123456789)
        self.assertEqual(self.tg_user1.tg_username, "test-tguser1")
        self.assertEqual(self.tg_user1.tg_first_name, "Test TgUser1")
        self.assertEqual(self.tg_user1.tg_last_name, "TgUser1")
        self.assertFalse(self.tg_user1.is_bot)
        self.assertIsNone(self.tg_user1.language_code)
        self.assertTrue(self.tg_user1.is_active)
        self.assertIsNotNone(self.tg_user1.created_at)
        self.assertIsNotNone(self.tg_user1.updated_at)
        self.assertEqual(self.tg_user2.id, 987654321)
        self.assertEqual(self.tg_user2.tg_username, "test-tguser2")
        self.assertEqual(self.tg_user2.tg_first_name, "Test TgUser2")
        self.assertEqual(self.tg_user2.tg_last_name, "TgUser2")
        self.assertTrue(self.tg_user2.is_bot)
        self.assertEqual(self.tg_user2.language_code, "en")
        self.assertTrue(self.tg_user2.is_active)
        self.assertIsNotNone(self.tg_user2.created_at)
        self.assertIsNotNone(self.tg_user2.updated_at)

    def test_tg_user_get_content_type(self):
        """Перевірка отримання ContentType для TgUser."""
        content_type = self.tg_user1.get_content_type()
        self.assertEqual(content_type.model, 'tguser')
        self.assertEqual(content_type.app_label, 'user_management')
