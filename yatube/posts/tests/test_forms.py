from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm, CommentForm
from ..models import Group, Post, User, Comment

User = get_user_model()


class TestForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа и ничего больше',
            slug='Test-group',
            description='Описание'
        )
        cls.user = User.objects.create_user(username='Testman')
        cls.post = Post.objects.create(
            text='Супер текст',
            author=cls.user,
            group=cls.group,
        )
        cls.forms = PostForm()
        cls.form_comment = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Супер текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertFalse(
            Post.objects.filter(
                text='Какой то текст для проверки',
                group=self.group.id,
                author=self.user
            ).exists()
        )

    def test_post_edit(self):
        """Если форма валидно, то вносятся изменения в пост"""
        form_data = {
            'text': 'Текст для проверки изменения поста',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertTrue(
            Post.objects.filter(
                text='Текст для проверки изменения поста',
                group=self.group.id,
                author=self.user
            ).exists()
        )

    def test_create_comment(self):
        comment_count = Comment.objects.count()
        form_data_for_comment = {
            'text': 'Тестовый текст',
            'author': TestForm.user,
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[
                TestForm.post.id]),
            data=form_data_for_comment,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[
                TestForm.post.id])
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый текст',
                author=TestForm.user,
            ).exists()
        )
