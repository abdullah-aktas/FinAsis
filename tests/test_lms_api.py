import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from decimal import Decimal

User = get_user_model()

@pytest.mark.django_db
def test_autograde_mcq_submission(client):
    # Create teacher and student
    teacher = User.objects.create_user(username='teacher', password='pass12345')
    student = User.objects.create_user(username='student', password='pass12345')

    api = APIClient()
    api.login(username='teacher', password='pass12345')

    # Create course
    course_resp = api.post('/api/v1/education/courses/', {
        'name': 'Math', 'code': 'M101', 'description': 'Basic', 'teacher': teacher.id
    }, format='json')
    assert course_resp.status_code in (200, 201), course_resp.content
    course_id = course_resp.data['id']

    # Create question (mcq), correct answer index 1
    q_resp = api.post('/api/v1/education/questions/', {
        'course': course_id,
        'text': '2+2?',
        'type': 'mcq',
        'points': '5.00',
        'choices': ['3', '4', '5'],
        'correct_answer': 1,
        'created_by': teacher.id
    }, format='json')
    assert q_resp.status_code in (200, 201), q_resp.content
    q_id = q_resp.data['id']

    # Create exam with that question
    exam_resp = api.post('/api/v1/education/exams/', {
        'course': course_id,
        'title': 'Quiz 1',
        'questions': [q_id],
        'duration_minutes': 10
    }, format='json')
    assert exam_resp.status_code in (200, 201), exam_resp.content
    exam_id = exam_resp.data['id']

    # Student submits answers
    api.logout()
    api.login(username='student', password='pass12345')
    sub_resp = api.post('/api/v1/education/exam-submissions/', {
        'exam': exam_id,
        'answers': {str(q_id): 1}
    }, format='json')
    assert sub_resp.status_code in (200, 201), sub_resp.content
    assert Decimal(sub_resp.data['auto_score']) == Decimal('5.00')

@pytest.mark.django_db
def test_autograde_bool_submission(client):
    teacher = User.objects.create_user(username='teacher2', password='pass12345')
    student = User.objects.create_user(username='student2', password='pass12345')

    api = APIClient()
    api.login(username='teacher2', password='pass12345')

    course_id = api.post('/api/v1/education/courses/', {
        'name': 'Logic', 'code': 'L101', 'description': 'Intro', 'teacher': teacher.id
    }, format='json').data['id']

    q_id = api.post('/api/v1/education/questions/', {
        'course': course_id,
        'text': 'Earth is round',
        'type': 'bool',
        'points': '2.00',
        'correct_answer': True,
        'created_by': teacher.id
    }, format='json').data['id']

    exam_id = api.post('/api/v1/education/exams/', {
        'course': course_id,
        'title': 'T/F',
        'questions': [q_id],
        'duration_minutes': 5
    }, format='json').data['id']

    api.logout()
    api.login(username='student2', password='pass12345')
    sub = api.post('/api/v1/education/exam-submissions/', {
        'exam': exam_id,
        'answers': {str(q_id): True}
    }, format='json')
    assert sub.status_code in (200, 201), sub.content
    assert Decimal(sub.data['auto_score']) == Decimal('2.00')
