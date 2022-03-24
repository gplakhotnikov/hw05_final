from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post

from django.core.cache import cache

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(CacheTests.user)

    def test_cache(self):
        post = Post.objects.create(
            author=CacheTests.user,
            group=None,
            text='Тестовый пост')
        index_page = self.authorized_client.get(reverse('posts:main')).content
        post.delete()
        index_page_cached = self.authorized_client.get(
            reverse('posts:main')).content
        self.assertEqual(index_page, index_page_cached)
        cache.clear()
        index_page_new = self.authorized_client.get(
            reverse('posts:main')).content
        self.assertNotEqual(index_page, index_page_new)
