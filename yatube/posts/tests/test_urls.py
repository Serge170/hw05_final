from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User

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
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )

        # Создаем пост от имени пользователя
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
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
            f'/posts/{self.post.id}/': ('posts/post_detail', HTTPStatus.OK),
            '/unixisting_page/': ('', HTTPStatus.NOT_FOUND),
        }

        for address, (template, status_code) in templates_url_all.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_author(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_author = {
            f'/posts/{self.post.id}/edit/': ('posts/create_post.html', HTTPStatus.OK),
        }

        for address, (template, status_code) in templates_url_author.items():
            with self.subTest(address=address):
                response = self.author.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_authorized_client(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url = {
            '/create/': ('posts/create_post.html', HTTPStatus.OK),
            '/follow/': ('posts/follow', HTTPStatus.OK),    
        }

        for address, (template, status_code) in templates_url.items():
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_post_create_guest(self):
        """Незарегистрированный пользователь не может создать пост"""
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_template_not_author(self):
        """Пользователь, не являющийся автором поста,
        не имеет доступа к странице редактирования.
        """
        response = self.client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_create_redirect_anonymous_on_login(self):
        """Страница 'posts/<int:post_id>/comment/' перенаправит
        анонимного пользователя на страницу логина."""
        form_comment_data = {
            'text': 'Новый комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.pk}
            ),
            data=form_comment_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.pk}/comment/'
        )

    def test_сommenting_is_not_available_to_an_anonymous_user(self):
        """Комментирование недоступно анонимному пользователю."""
        form_comment_data = {
            'text': 'Новый комментарий',
        }
        response_not_authorized = self.guest_client.get(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.pk}
            ),
            data=form_comment_data
        )
        self.assertEqual(
            response_not_authorized.status_code,
            HTTPStatus.FOUND.value)