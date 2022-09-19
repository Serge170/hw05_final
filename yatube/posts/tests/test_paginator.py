import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

COUNT_TEST_POSTS = 17
NUMBER_OF_POSTS: int = 10

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PaginatorViewsTest(TestCase):
    """Проверка Paginator."""
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Автор поста
        cls.author = User.objects.create_user(username='author')
        cls.post_author = Client()
        cls.post_author.force_login(cls.author)
        cache.clear()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создание 17 постов
        for i in range(COUNT_TEST_POSTS):
            Post.objects.bulk_create([Post(author=cls.author,
                                      text=f'Тестовый пост № {i}',
                                      group=cls.group)
                                      ])

    def test_pages_contain_correct_records(self):
        """Проверка количества постов на первой и второй страницах."""
        paginator_pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            )
        ]
        for url in paginator_pages:
            with self.subTest(url=url):
                first_response = self.post_author.get(url)
                second_response = self.post_author.get((url) + '?page=2')
                self.assertEqual(len(
                    first_response.context['page_obj']),
                    NUMBER_OF_POSTS
                )
                self.assertEqual(len(
                    second_response.context['page_obj']),
                    COUNT_TEST_POSTS - NUMBER_OF_POSTS
                )
