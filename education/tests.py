from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Category, Course, Lesson, Enrollment

# Create your tests here.

class CategoryModelTest(TestCase):
    def test_str(self):
        category = Category.objects.create(name='Test Kategori')
        self.assertEqual(str(category), 'Test Kategori')

class CourseModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Kategori')
        self.course = Course.objects.create(
            title='Test Kurs',
            description='Açıklama',
            category=self.category,
            level='beginner',
            duration=10
        )
    def test_str(self):
        self.assertEqual(str(self.course), 'Test Kurs')

class LessonModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Kategori')
        self.course = Course.objects.create(
            title='Test Kurs',
            description='Açıklama',
            category=self.category,
            level='beginner',
            duration=10
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Ders 1',
            content='İçerik',
            order=1
        )
    def test_str(self):
        self.assertEqual(str(self.lesson), 'Test Kurs - Ders 1')

class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Kategori')
        self.course = Course.objects.create(
            title='Test Kurs',
            description='Açıklama',
            category=self.category,
            level='beginner',
            duration=10
        )
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
    def test_str(self):
        self.assertIn('Test Kurs', str(self.enrollment))

class CourseListViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Kategori')
        Course.objects.create(title='Test Kurs', description='Açıklama', category=self.category, level='beginner', duration=10)
    def test_course_list_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('education:course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Kurs')
