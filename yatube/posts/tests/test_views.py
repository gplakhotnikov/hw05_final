import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test2',
            description='Тестовое описание2',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='s.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=None,
            text='Самый первый тестовый пост',
        )
        cls.post2 = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)

    def test_pages_template(self):
        group_slug = PostsPagesTests.group.slug
        username = PostsPagesTests.user.username
        post_id = PostsPagesTests.post.id
        templates_pages_names = {
            reverse('posts:main'): 'posts/index.html',
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': group_slug}):
                    'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': username}):
                    'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': post_id}):
                    'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': post_id}):
                    'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_check(self, post):
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.author.username, PostsPagesTests.user.username)
        self.assertEqual(post.group, PostsPagesTests.group)
        self.assertEqual(post.image, PostsPagesTests.post2.image)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:main'))
        response_2 = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        post_2 = response_2.context['page_obj'][0]
        self.post_check(post)
        self.post_check(post_2)

    def test_group_page(self):
        group_slug = PostsPagesTests.group.slug
        response = (self.authorized_client.
                    get(reverse(
                        'posts:group_list', kwargs={'slug': group_slug})))
        post = response.context['page_obj'][0]
        group = response.context['group']
        self.post_check(post)
        self.assertEqual(PostsPagesTests.group, group)

    def test_profile_page_correct_context(self):
        username = PostsPagesTests.user.username
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': username})))
        post = response.context['page_obj'][0]
        self.post_check(post)

    def test_post_detail_show_correct_context(self):
        post_id = PostsPagesTests.post2.id
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': post_id})))
        post = response.context['post']
        self.post_check(post)

    def test_edit_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_create_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_show_on_template(self):
        group_slug = PostsPagesTests.group.slug
        group_slug2 = PostsPagesTests.group2.slug
        username = PostsPagesTests.user.username
        templates_pages_names = {
            'main': reverse('posts:main'),
            'group': reverse(
                'posts:group_list', kwargs={'slug': group_slug}),
            'profile': reverse(
                'posts:profile', kwargs={'username': username})
        }
        for page, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTrue(
                    self.post2 in response.context['page_obj'].object_list
                )
        response = (self.authorized_client.
                    get(reverse(
                        'posts:group_list', kwargs={'slug': group_slug2})))
        self.assertTrue(
            self.post2 not in response.context['page_obj'].object_list
        )

    def test_show_comment_on_template(self):
        form_data = {
            'post': PostsPagesTests.post,
            'text': 'Да чушь собачья!',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostsPagesTests.post.id}),
            data=form_data,
            follow=True,
        )
        comment = response.context['comments'][0]
        self.assertEqual(comment.post.id, PostsPagesTests.post.id)
        self.assertEqual(comment.author.username,
                         PostsPagesTests.user.username)
        self.assertEqual(comment.text, 'Да чушь собачья!')


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        for i in range(15):
            cls.post2 = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый пост' + str(i + 1),
            )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTests.user)

    def test_first_index_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_index_page_contains_five_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_group_page_contains_ten_records(self):
        group_slug = PaginatorTests.group.slug
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': group_slug})))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_page_contains_five_records(self):
        group_slug = PaginatorTests.group.slug
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': group_slug})
                        + '?page=2'))
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_profile_page_contains_ten_records(self):
        username = PaginatorTests.user.username
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': username})))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_five_records(self):
        username = PaginatorTests.user.username
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': username}) + '?page=2'))
        self.assertEqual(len(response.context['page_obj']), 5)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='user_1')
        cls.user_2 = User.objects.create_user(username='user_2')

    def setUp(self):
        cache.clear()
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(FollowTests.user_1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(FollowTests.user_2)

    def test_follow(self):
        (self.authorized_client_1.
            get(reverse('posts:profile_follow',
                kwargs={'username': FollowTests.user_2})))
        followed_user = (FollowTests.
                         user_1.follower.all().values_list('author',
                                                           flat=True)[0])
        self.assertEqual(followed_user, FollowTests.user_2.id)

    def test_unfollow(self):
        (self.authorized_client_1.
            get(reverse('posts:profile_follow',
                kwargs={'username': FollowTests.user_2})))
        (self.authorized_client_1.
            get(reverse('posts:profile_unfollow',
                kwargs={'username': FollowTests.user_2})))
        followed_list = (FollowTests.
                         user_1.follower.all().values_list('author',
                                                           flat=True))
        self.assertFalse(followed_list.exists())

    def test_new_entry_appears_for_proper_user(self):
        (self.authorized_client_1.
            get(reverse('posts:profile_follow',
                kwargs={'username': FollowTests.user_2})))
        post = Post.objects.create(
            author=FollowTests.user_2,
            group=None,
            text='Тестовый пост',)
        response = (self.authorized_client_1.
                    get(reverse('posts:follow_index')))
        self.assertTrue(
            post in response.context['page_obj'].object_list)
        self.assertEqual(post, response.context['page_obj'][0])

    def test_new_entry_not_appear_for_inproper_user(self):
        (self.authorized_client_1.
            get(reverse('posts:profile_follow',
                kwargs={'username': FollowTests.user_2})))
        post = Post.objects.create(
            author=FollowTests.user_2,
            group=None,
            text='Тестовый пост',)
        response = (self.authorized_client_2.
                    get(reverse('posts:follow_index'))).context['page_obj']
        self.assertTrue(
            post not in response.object_list)
