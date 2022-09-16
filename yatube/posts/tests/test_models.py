from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        group_title = group.title
        post = PostModelTest.post
        post_title = post.text[:15]
        expected_str = {
            group: group_title,
            post: post_title
        }
        for model, expected_value in expected_str.items():
            with self.subTest(model=model):
                self.assertEqual(expected_value, str(model))

    def test_models_have_correct_verbose_name(self):
        """Verbose_name в полях модели Post совпадает с ожидаемым."""

        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор поста',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""

        post = PostModelTest.post
        field_help_texts = {
            'text': 'Напишите содержимое поста',
            'group': 'Здесь можно выбрать группу',
        }

        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
