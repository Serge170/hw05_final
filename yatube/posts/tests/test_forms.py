import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateForm(TestCase):
    """Проверка формы со странице создания поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        picture = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='picture.gif',
            content=picture,
            content_type='image/gif'
        )

        cls.user = User.objects.create_user(username='author')
        cls.author = Client()
        cls.author.force_login(PostCreateForm.user)
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
            image=cls.uploaded,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.author = Client()
        self.author.force_login(PostCreateForm.user)

    def test_post_create(self):
        """Форма Post создает запись."""
        # Подсчет количества записей в Post
        posts_count = Post.objects.count()
        last_post = Post.objects.all().first()
        new_post = Post.objects.filter(
            text='Текст поста из формы',
            group=self.group.pk,
        )
        form_data = {
            'text': 'Текст поста из формы',
            'group': self.group.pk,
            'author': self.user.username,
            'image': self.post.image,
        }
        # Отправляем POST-запрос
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(new_post.exists())
        self.assertEqual(
            Post.objects.all().order_by('created').first(),
            last_post
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            args=[self.user.username]
        ))
        new_post = Post.objects.last()
        self.assertEqual(
            new_post.author,
            self.user
        )
        self.assertEqual(
            new_post.group,
            self.group
        )

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

        old_group_response = self.authorized_user.get(
            reverse(
                'group:group_list',
                args=(self.group.slug, ))
        )
        self.assertNotEqual(old_group_response, [0]
                            )
