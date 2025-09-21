from django.test import TestCase
from src.apps.education.models import FinancialTermCard, LearningContent, Badge, Forum
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

# Create your tests here.

class FinancialTermCardModelTest(TestCase):
    def test_create_card(self):
        card = FinancialTermCard.objects.create(term='Bilanço', description='Bir işletmenin mali durumu.', example='Örnek bilanço tablosu.')
        self.assertEqual(str(card), 'Bilanço')
        self.assertEqual(card.description, 'Bir işletmenin mali durumu.')

class LearningContentModelTest(TestCase):
    def test_create_content(self):
        user = User.objects.create(username='testuser')
        content = LearningContent.objects.create(title='Test Video', description='Açıklama', content_type='video', created_by=user)
        self.assertEqual(str(content), 'Test Video')
        self.assertEqual(content.content_type, 'video')

class BadgeModelTest(TestCase):
    def test_create_badge(self):
        badge = Badge.objects.create(name='Başarı Rozeti', description='10 quiz tamamla', icon='badges/test.png', criteria={'quizzes': 10})
        self.assertEqual(str(badge), 'Başarı Rozeti')

class ForumModelTest(TestCase):
    def test_create_forum(self):
        user = User.objects.create(username='forumuser')
        forum = Forum.objects.create(title='Genel Forum', description='Genel tartışmalar', created_by=user)
        self.assertEqual(str(forum), 'Genel Forum')

class LearningContentAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='test123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        LearningContent.objects.create(title='API Video', description='API test', content_type='video', created_by=self.user)
    def test_list_content(self):
        response = self.client.get('/education/api/learning-content/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.data or isinstance(response.data, list))
