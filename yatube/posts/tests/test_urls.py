from django.contrib.auth import get_user_model
from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class TestUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тут что-то есть',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user2 = User.objects.create_user(username='Testman')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(TestUrls.user)

    def test_urls_for_guest(self):
        """Тест страниц для гостя"""
        _http_status = 302
        urls = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/posts/create/': HTTPStatus.NOT_FOUND,
            f'/posts/{self.post.id}/edit/': _http_status,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            f'posts/{self.post.id}/comment': HTTPStatus.NOT_FOUND,
            f'profile/{self.user2}/follow': HTTPStatus.NOT_FOUND,
            f'profile/{self.user2}/unfollow': HTTPStatus.NOT_FOUND
        }
        for url, status_code in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_post_create_for_authorized_user(self):
        """
        Тест страницы создания поста
        для авторизованного пользователя
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_for_author_user(self):
        """
        Тест страницы редактирования поста
        для автора поста
        """
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_for_authorized_user(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_for_author(self):
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow(self):
        response = self.authorized_client.get(f'/profile/{self.user2}/follow/')
        self.assertRedirects(
            response, f'/profile/{self.user2}/'
        )

    def test_unfollow(self):
        response = self.authorized_client.get(
            f'/profile/{self.user2}/unfollow/')
        self.assertRedirects(
            response, f'/profile/{self.user2}/'
        )
