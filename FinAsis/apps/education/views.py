# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import FinancialTermCard, StudentAnalytics, Badge, Level, StudentGamificationProgress, LearningContent, Forum, ForumTopic, ForumPost, GroupAssignment, Feedback
from .forms import FinancialTermCardForm
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, filters
from .serializers import StudentAnalyticsSerializer, BadgeSerializer, LevelSerializer, StudentGamificationProgressSerializer, LearningContentSerializer, ForumSerializer, ForumTopicSerializer, ForumPostSerializer, GroupAssignmentSerializer, FeedbackSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .services import AdaptiveLearningService
from rest_framework.permissions import IsAdminUser, AllowAny

@login_required
def kobi_tutorials(request):
    return render(request, 'education/kobi_tutorials.html')

@login_required
def index(request):
    return render(request, 'education/index.html')

@login_required
def education_home(request):
    return render(request, "education/education_home.html")

@method_decorator(login_required, name='dispatch')
class FinancialTermCardListView(ListView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_list.html'
    context_object_name = 'cards'

@method_decorator(login_required, name='dispatch')
class FinancialTermCardDetailView(DetailView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_detail.html'
    context_object_name = 'card'

@method_decorator(login_required, name='dispatch')
class FinancialTermCardCreateView(CreateView):
    model = FinancialTermCard
    form_class = FinancialTermCardForm
    template_name = 'education/financialtermcard_form.html'
    success_url = reverse_lazy('education:financialtermcard_list')

@method_decorator(login_required, name='dispatch')
class FinancialTermCardUpdateView(UpdateView):
    model = FinancialTermCard
    form_class = FinancialTermCardForm
    template_name = 'education/financialtermcard_form.html'
    success_url = reverse_lazy('education:financialtermcard_list')

@method_decorator(login_required, name='dispatch')
class FinancialTermCardDeleteView(DeleteView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_confirm_delete.html'
    success_url = reverse_lazy('education:financialtermcard_list')

class StudentAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['date', 'completed_assignments', 'completed_quizzes', 'success_rate']
    search_fields = ['weak_topics', 'strong_topics']

    def get_queryset(self):
        return StudentAnalytics.objects.filter(student=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def adaptive_recommendation_api(request):
    """
    Öğrencinin zayıf olduğu konulara göre kişiselleştirilmiş öneriler döner.
    """
    service = AdaptiveLearningService()
    result = service.get_recommendations(request.user)
    return Response(result)

class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated]

class StudentGamificationProgressViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentGamificationProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return StudentGamificationProgress.objects.filter(student=self.request.user)

class LearningContentViewSet(viewsets.ModelViewSet):
    queryset = LearningContent.objects.all()
    serializer_class = LearningContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'title', 'content_type']
    search_fields = ['title', 'description', 'extra_note']

class ForumViewSet(viewsets.ModelViewSet):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'title']
    search_fields = ['title', 'description']

class ForumTopicViewSet(viewsets.ModelViewSet):
    queryset = ForumTopic.objects.all()
    serializer_class = ForumTopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'title']
    search_fields = ['title']

class ForumPostViewSet(viewsets.ModelViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at']
    search_fields = ['content']
    def get_queryset(self):
        return ForumPost.objects.filter(author=self.request.user)

class GroupAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = GroupAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'title']
    search_fields = ['title', 'description']
    def get_queryset(self):
        return GroupAssignment.objects.filter(members=self.request.user)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()] 