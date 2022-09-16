from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post, User

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    """Проверка доступности страниц и названий шаблонов приложения posts.
    учитывается уровень доступа. Несуществующая страница возвращает ошибку 404.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.author = Client()
        cls.author.force_login(PostURLTests.user)

        # Создаем группу
        Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )

        # Создаем пост от имени пользователя
        Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            pk=1
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.author = Client()
        self.author.force_login(PostURLTests.user)

    def test_urls_for_all(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_all = {
            '/': ('posts/index', HTTPStatus.OK),
            '/group/test-group/': ('posts/group_list', HTTPStatus.OK),
            '/profile/author/': ('posts/profile', HTTPStatus.OK),
            '/posts/1/': ('posts/post_detail', HTTPStatus.OK),
            '/unixisting_page/': ('', HTTPStatus.NOT_FOUND),
        }

        for address, (template, status_code) in templates_url_all.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_author(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_author = {
            '/posts/1/edit/': ('posts/create_post.html', HTTPStatus.OK),
        }

        for address, (template, status_code) in templates_url_author.items():
            with self.subTest(address=address):
                response = self.author.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_authorized_client(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url = {
            '/create/': ('posts/create_post.html', HTTPStatus.OK),
        }

        for address, (template, status_code) in templates_url.items():
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertEqual(response.status_code, status_code)
