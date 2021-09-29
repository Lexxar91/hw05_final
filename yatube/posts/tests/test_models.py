from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Супер группа',
        )

    def test_models_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        text_post = post.text[:15]
        self.assertEqual(text_post, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Супер группа',
            slug='Супер группа',
            description='Супер описание',
        )

    def test_check_group(self):
        group = GroupModelTest.group
        title_group = group.title
        self.assertEqual(title_group, str(group))
