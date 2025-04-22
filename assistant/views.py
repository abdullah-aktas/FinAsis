from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Avg
from django.core.cache import cache
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    ChatSession, ChatMessage, PagePrompt, UserPreference,
    AssistantCapability, AssistantPerformance
)
from .serializers import (
    ChatSessionSerializer, ChatMessageSerializer,
    PagePromptSerializer, UserPreferenceSerializer,
    AssistantCapabilitySerializer, AssistantPerformanceSerializer
)
from .filters import ChatSessionFilter, ChatMessageFilter, PagePromptFilter
from .permissions import IsOwnerOrReadOnly
from .services import AssistantService
import json
import logging

logger = logging.getLogger(__name__)

class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filterset_class = ChatSessionFilter

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        session = self.get_object()
        content = request.data.get('content')
        message_type = request.data.get('message_type', 'text')
        
        if not content:
            return Response(
                {'error': 'Mesaj içeriği gereklidir'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            assistant_service = AssistantService()
            response = assistant_service.process_message(
                session=session,
                content=content,
                message_type=message_type
            )
            return Response(response)
        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {str(e)}")
            return Response(
                {'error': 'Mesaj işlenirken bir hata oluştu'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        session = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(ChatSession.STATUS_CHOICES):
            return Response(
                {'error': 'Geçersiz durum'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = new_status
        session.save()
        return Response({'status': 'Durum güncellendi'})

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filterset_class = ChatMessageFilter

    def get_queryset(self):
        return self.queryset.filter(session__user=self.request.user)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        message = self.get_object()
        try:
            assistant_service = AssistantService()
            new_response = assistant_service.regenerate_response(message)
            return Response(new_response)
        except Exception as e:
            logger.error(f"Yeniden oluşturma hatası: {str(e)}")
            return Response(
                {'error': 'Yanıt yeniden oluşturulurken bir hata oluştu'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PagePromptViewSet(viewsets.ModelViewSet):
    queryset = PagePrompt.objects.all()
    serializer_class = PagePromptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = PagePromptFilter

    @action(detail=False, methods=['get'])
    def get_by_path(self, request):
        page_path = request.query_params.get('path')
        if not page_path:
            return Response(
                {'error': 'Sayfa yolu gereklidir'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prompt = get_object_or_404(PagePrompt, page_path=page_path, is_active=True)
        serializer = self.get_serializer(prompt)
        return Response(serializer.data)

class UserPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.queryset.get_or_create(user=self.request.user)[0]

    @action(detail=True, methods=['post'])
    def update_capabilities(self, request, pk=None):
        preference = self.get_object()
        capabilities = request.data.get('capabilities', [])
        
        try:
            preference.enabled_capabilities.set(capabilities)
            return Response({'status': 'Yetenekler güncellendi'})
        except Exception as e:
            logger.error(f"Yetenek güncelleme hatası: {str(e)}")
            return Response(
                {'error': 'Yetenekler güncellenirken bir hata oluştu'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AssistantCapabilityViewSet(viewsets.ModelViewSet):
    queryset = AssistantCapability.objects.filter(is_active=True)
    serializer_class = AssistantCapabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

class AssistantPerformanceViewSet(viewsets.ModelViewSet):
    queryset = AssistantPerformance.objects.all()
    serializer_class = AssistantPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(session__user=self.request.user)

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        user_performance = self.get_queryset().aggregate(
            avg_response_time=Avg('response_time'),
            avg_token_count=Avg('token_count'),
            avg_feedback=Avg('user_feedback')
        )
        return Response(user_performance)

class ChatSessionListView(LoginRequiredMixin, ListView):
    model = ChatSession
    template_name = 'assistant/chat_session_list.html'
    context_object_name = 'sessions'
    paginate_by = 10

    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user
        ).order_by('-last_activity')

class ChatSessionDetailView(LoginRequiredMixin, DetailView):
    model = ChatSession
    template_name = 'assistant/chat_session_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.all().order_by('created_at')
        return context

class PagePromptListView(LoginRequiredMixin, ListView):
    model = PagePrompt
    template_name = 'assistant/page_prompt_list.html'
    context_object_name = 'prompts'
    paginate_by = 10

    def get_queryset(self):
        return PagePrompt.objects.filter(is_active=True).order_by('-priority')

class UserPreferenceUpdateView(LoginRequiredMixin, UpdateView):
    model = UserPreference
    template_name = 'assistant/user_preference_form.html'
    fields = ['language', 'voice_style', 'response_speed']
    success_url = reverse_lazy('assistant:preference-update')

    def get_object(self):
        return UserPreference.objects.get_or_create(user=self.request.user)[0]

@require_http_methods(["POST"])
@csrf_exempt
def process_chat_message(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        content = data.get('content')
        message_type = data.get('message_type', 'text')

        if not all([session_id, content]):
            return JsonResponse(
                {'error': 'Eksik parametreler'},
                status=400
            )

        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        assistant_service = AssistantService()
        
        response = assistant_service.process_message(
            session=session,
            content=content,
            message_type=message_type
        )
        
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Mesaj işleme hatası: {str(e)}")
        return JsonResponse(
            {'error': 'Mesaj işlenirken bir hata oluştu'},
            status=500
        ) 