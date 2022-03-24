from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from posts.models import Group, Post

from django.core.cache import cache

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user0 = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user0,
            text='Тестовый пост',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client0 = Client()
        self.authorized_client0.force_login(PostsURLTests.user0)
        self.user = User.objects.create_user(username='User1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_index(self):
        response = self.guest_client.get('/index')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_page(self):
        response = self.guest_client.get('/group/test/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_page(self):
        response = self.authorized_client.get('/profile/test/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_page(self):
        post = PostsURLTests.post
        id = post.id
        response = self.guest_client.get(f'/posts/{id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page_guest(self):
        post = PostsURLTests.post
        id = post.id
        response = self.guest_client.get(f'/posts/{id}/edit/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/1/edit/')
        )

    def test_post_edit_page_other_user(self):
        post = PostsURLTests.post
        id = post.id
        response = self.authorized_client.get(
            f'/posts/{id}/edit/', follow=True)
        self.assertRedirects(
            response, f'/posts/{id}/'
        )

    def test_post_edit_page_correct_user(self):
        post = PostsURLTests.post
        id = post.id
        response = self.authorized_client0.get(
            f'/posts/{id}/edit/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_page_guest(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/')
        )

    def test_create_page(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_nonexisting_page(self):
        response = self.guest_client.get('/theory/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        post = PostsURLTests.post
        id = post.id
        post_url = f'/posts/{id}/'
        post_edit_url = f'/posts/{id}/edit/'
        templates_url_names = {
            '/': 'posts/index.html',
            '/index': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/test/': 'posts/profile.html',
            post_url: 'posts/post_detail.html',
            post_edit_url: 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client0.get(address)
                self.assertTemplateUsed(response, template)
