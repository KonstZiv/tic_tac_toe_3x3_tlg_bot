from django.test import TestCase

from user_management.models import User


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@user.user",
            password="user1_password",
        )
        self.user2 = User.objects.create_user(
            email="user2@user.user",
            password="user2_password",
            username="user2",
            is_staff=True,
        )
        self.user3 = User.objects.create_user(
            email="user3@user.user",
            password="user3_password",
            username="user3",
            first_name="User3",
            last_name="Test",
        )
        self.super_user = User.objects.create_superuser(
            email="super_user@user.user",
            password="super_password",
        )

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
        self.super_user.delete()

    def test_user_creation(self):
        """Перевірка створення користувача з обов'язковими полями."""
        self.assertEqual(self.user1.email, "user1@user.user")
        self.assertTrue(self.user1.check_password("user1_password"))

    def test_user_with_username(self):
        """Перевірка створення користувача з username."""
        self.assertEqual(self.user2.email, "user2@user.user")
        self.assertEqual(self.user2.username, "user2")
        self.assertTrue(self.user2.check_password("user2_password"))
        # Перевірка, що не є staff (незалежно від is_staff при створенні)
        self.assertFalse(self.user2.is_staff)
        self.assertEqual(self.user2.username, "user2")

    def test_user_with_full_name(self):
        """Перевірка створення користувача з іменем та прізвищем."""
        self.assertEqual(self.user3.email, "user3@user.user")
        self.assertEqual(self.user3.first_name, "User3")
        self.assertEqual(self.user3.last_name, "Test")

    def test_superuser_creation(self):
        """Перевірка створення суперкористувача."""
        self.assertEqual(self.super_user.email, "super_user@user.user")
        self.assertTrue(self.super_user.is_staff)
        self.assertTrue(self.super_user.is_superuser)

    def test_user_get_content_type(self):
        """Перевірка отримання ContentType для User."""
        content_type = self.user1.get_content_type()
        self.assertIsNotNone(content_type)
        self.assertEqual(content_type.model, 'user')
