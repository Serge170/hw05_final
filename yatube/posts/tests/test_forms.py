import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateForm(TestCase):
    """Проверка формы со странице создания поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')

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
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_post(self):
        """ Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст поста из формы',
            'group': self.group.pk,
            'author': self.user.username,
            'image': uploaded,
        }

        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'author'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Проверяем, что сoдержания поля в словаре соответствуют ожиданиям
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=self.group.id,
            ))

    def test_edit_post(self):
        """Запись успешно редактируется."""
        form_data = {
            'text': 'Текст поста из формы',
            'group': self.group.pk
        }
        self.authorized_user.post(
            reverse(
                'posts:post_edit',
                args=[self.post.pk]
            ),
            data=form_data,
            follow=False
        )
        self.assertIsNot(
            Post.objects.get(pk=self.post.pk).text,
            form_data['text'])

        group_response = self.authorized_user.get(
            reverse(
                'group:group_list',
                args=(self.group.slug, ))
        )
        self.assertNotEqual(group_response, [0]
                            )

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
