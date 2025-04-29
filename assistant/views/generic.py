# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from .services.ai_core import AIAssistant
from .models import ChatSession, ChatMessage

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ask_assistant(request):
    try:
        data = json.loads(request.body)
        message = data.get('message')
        page_context = data.get('page_context', {})
        
        if not message:
            return JsonResponse({'error': 'Mesaj boş olamaz'}, status=400)
            
        assistant = AIAssistant()
        
        # Aktif oturumu bul veya yeni oluştur
        active_session = ChatSession.objects.filter(
            user=request.user,
            is_active=True
        ).first()
        
        if not active_session:
            active_session = assistant.create_chat_session(request.user, page_context)
            
        # Kullanıcı mesajını kaydet
        assistant.save_message(active_session, message)
        
        # Chat geçmişini al
        chat_history = ChatMessage.objects.filter(session=active_session).order_by('created_at')[:10]
        
        # Yanıt oluştur
        response = assistant.generate_response(message, page_context, chat_history)
        
        # Asistan yanıtını kaydet
        assistant.save_message(active_session, response, is_user=False)
        
        return JsonResponse({
            'reply': response,
            'session_id': active_session.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_chat_history(request, session_id):
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        
        return JsonResponse({
            'messages': [
                {
                    'content': msg.content,
                    'is_user': msg.is_user,
                    'created_at': msg.created_at.isoformat()
                }
                for msg in messages
            ]
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Oturum bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 