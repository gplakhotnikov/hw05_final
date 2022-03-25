from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        expected_post_name = post.text
        verbose_name = post._meta.get_field('text').verbose_name
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(expected_post_name, str(post))
        self.assertEqual(verbose_name, 'Текст поста')
        self.assertEqual(help_text, 'Введите текст поста')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        group = GroupModelTest.group
        expected_group_name = group.title
        verbose_name = group._meta.get_field('title').verbose_name
        help_text = group._meta.get_field('title').help_text
        self.assertEqual(expected_group_name, str(group))
        self.assertEqual(verbose_name, 'Название группы')
        self.assertEqual(help_text, 'Введите название группы')


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_models_have_correct_object_names(self):
        follow = FollowModelTest.follow
        expected_follower = follow.user
        expected_following = follow.author
        verbose_name_1 = follow._meta.get_field('user').verbose_name
        verbose_name_2 = follow._meta.get_field('author').verbose_name
        self.assertEqual(expected_follower, FollowModelTest.user)
        self.assertEqual(expected_following, FollowModelTest.author)
        self.assertEqual(verbose_name_1, 'Пользователь, который подписывается')
        self.assertEqual(verbose_name_2,
                         'Пользователь, на которого подписываются')
