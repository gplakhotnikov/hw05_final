import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа Котики',
            slug='cats',
            description='Группа про котиков',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Создаем новый пост про котиков',
            'group': PostFormTests.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.user}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Создаем новый пост про котиков',
                group=self.group,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        post = Post.objects.create(
            author=PostFormTests.user,
            group=None,
            text='Тестовый пост',
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный пост!',
            'group': PostFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{post.id}'}
            ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Отредактированный пост!',
                group=PostFormTests.group.id,
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый пост',
                group=None,
            ).exists()
        )


class CommentsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост для добавления комментариев',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentsTests.user)

    def test_post_comment_authorized(self):
        comments_n = CommentsTests.post.comments.count()
        form_data = {
            'post': CommentsTests.post,
            'text': 'Не согласен! Чушь полная',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': CommentsTests.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': CommentsTests.post.id}))
        self.assertEqual(CommentsTests.post.comments.count(), comments_n + 1)

    def test_post_comment_guest(self):
        comment_count = CommentsTests.post.comments.count()
        form_data = {
            'post': CommentsTests.post,
            'text': 'Не согласен! Чушь полная',
        }
        self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': CommentsTests.post.id}),
            data=form_data,
            follow=True,)
        self.assertEqual(CommentsTests.post.comments.count(), comment_count)
