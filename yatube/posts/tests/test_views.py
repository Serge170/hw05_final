import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

COUNT_TEST_POSTS = 17
NUMBER_OF_POSTS: int = 10

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    """ Создаем тестовую среду"""
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
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
            group=cls.group,
            image=uploaded,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        cache.clear()

    def test_pages_guest_client_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Проверяем используемые шаблоны
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-group'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'author'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:profile', kwargs={'username': 'author'}):
            'posts/profile.html',
        }
        # Проверка, при обращении к name вызывается соответствующий HTML-шаблон
        for reverse_name, address in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, address)

    def test_pages_author_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Проверяем используемые шаблоны
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:post_edit', kwargs={'post_id': 1}):
            'posts/create_post.html',
        }
        # Проверка, при обращении к name вызывается соответствующий HTML-шаблон
        for reverse_name, address in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, address)

    def test_views_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом.
        context - это список постов. Проверяем первый элемент
        """
        response = self.authorized_user.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'][0].id, self.post.id)

    def test_group_list_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse(
            'posts:group_list',
            args=[self.group.slug]
        ))
        response_post = response.context.get('page_obj').object_list[0]
        views_context = {
            response_post.author: self.post.author,
            response_post.group: self.post.group,
            response_post.text: self.post.text,
            response_post.image: self.post.image,
        }
        for view_response, name in views_context.items():
            with self.subTest(name=name):
                self.assertEqual(view_response, name)

    def test_views_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом.
        context - это список постов. Проверяем первый элемент и author
        """
        response = self.authorized_user.get(reverse('posts:profile',
                                            kwargs={'username': 'author'}))
        first_object = response.context['page_obj'][0]
        views_context = {
            first_object.author: self.post.author,
            first_object.group: self.post.group,
            first_object.text: self.post.text,
            first_object.image: self.post.image,
        }
        for view_response, name in views_context.items():
            with self.subTest(name=name):
                self.assertEqual(view_response, name)

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse(
            'posts:post_detail',
            args=[self.post.id]
        ))
        response_post = response.context['posts']
        views_context = {
            response_post.author: self.post.author,
            response_post.group: self.post.group,
            response_post.text: self.post.text,
            response_post.image: self.post.image,
            response_post: self.post,
        }
        for view_response, name in views_context.items():
            with self.subTest(name=name):
                self.assertEqual(view_response, name)

    def test_post_create_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse(
            'posts:post_edit',
            args=[self.post.id]
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_extra(self):
        """Проверьте, что если при создании поста указать группу,
        то этот пост появляется на главной странице сайта,
        на странице выбранной группы,в профайле пользователя.
        Проверьте, что этот пост не попал в группу,
        для которой не был предназначен."""

        response = self.authorized_user.get(reverse('posts:index'))
        context = response.context['page_obj']
        self.assertIn(self.post, context)

        response = self.authorized_user.get(reverse('posts:group_list',
                                            kwargs={'slug': 'test-group'}))
        context = response.context['page_obj']
        self.assertIn(self.post, context)

        response = self.authorized_user.get(reverse('posts:profile',
                                            kwargs={'username': 'author'}))
        context = response.context['page_obj']
        self.assertIn(self.post, context)

    def test_comment_autor(self):
        """Комментировать посты может только авторизованный пользователь
        После успешной отправки комментарий появляется на странице поста"""

        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='Тестовый комментарий',
        )
        response = self.authorized_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        comment = response.context['comments'][0]
        text = comment.text
        self.assertEqual(text, self.comment.text)

    def test_cache_index(self):
        """Главная страница работает с 20 секундным кешем."""
        self.authorized_user.get(
            reverse('posts:index'))
        Post.objects.create(
            author=self.user,
            text='текст 1',
            group=self.group)
        response1 = self.authorized_user.get(
            reverse('posts:index'))
        Post.objects.all().delete()
        response2 = self.authorized_user.get(
            reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.authorized_user.get(
            reverse('posts:index'))
        self.assertNotEqual(response1.content, response3.content)

    def test_authorized_user_follow(self):
        """Тестирование подписки на автора"""
        self.author = User.objects.create(username='NoNameAuthor')
        follow_count_before = self.user.follower.count()
        self.authorized_user.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.assertEqual(self.user.follower.count(), follow_count_before + 1)
        self.authorized_user.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )

    def test_authorized_user_unfollow(self):
        """Тестирование отписки на автора"""
        self.author = User.objects.create(username='NoNameAuthor')
        follow_count_before = self.user.follower.count()
        self.authorized_user.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.authorized_user.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )
        self.assertEqual(self.user.follower.count(), follow_count_before)

    def test_follow_page(self):
        """Проверка, что пост появляется у того, кто на него подписан.
        И не появляется у тех, кто не подписан"""
        self.author = User.objects.create(username='NoNameAuthor')
        self.authorized_user.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.follow_post = Post.objects.create(
            author=self.author,
            text='Тестовый текст подписки',
            group=self.group,
        )
        response = self.authorized_user.get(reverse('posts:follow_index'))
        self.assertEqual(response.context.get(
            'page_obj').object_list[0].text, 'Тестовый текст подписки'
        )
        self.authorized_user.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )
        response = self.authorized_user.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context.get('page_obj').object_list.count(), 0)
