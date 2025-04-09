from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import logging
from .services import FinancialAIService, ChatAIService

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def ai_home(request):
    """AI asistanı ana sayfası"""
    return render(request, 'ai_assistant/home.html')

@login_required
def ai_chat(request):
    """AI sohbet sayfası"""
    return render(request, 'ai_assistant/chat.html')

@login_required
def financial_analysis(request):
    """Finansal analiz sayfası"""
    return render(request, 'ai_assistant/analysis.html')

@login_required
def recommendations(request):
    """Öneriler sayfası"""
    return render(request, 'ai_assistant/recommendations.html')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_financial_data(request):
    """Finansal veri analizi API endpoint'i"""
    try:
        service = FinancialAIService()
        results = service.analyze_financial_data(request.user, request.data)
        return Response(results)
    except Exception as e:
        logger.error(f"Finansal analiz hatası: {str(e)}")
        return Response(
            {"error": "Analiz sırasında bir hata oluştu."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_ai_recommendations(request):
    """Kişiselleştirilmiş öneriler API endpoint'i"""
    try:
        service = FinancialAIService()
        recommendations = service.get_personalized_recommendations(request.user, request.data)
        return Response({"recommendations": recommendations})
    except Exception as e:
        logger.error(f"Öneri oluşturma hatası: {str(e)}")
        return Response(
            {"error": "Öneriler oluşturulurken bir hata oluştu."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_market_trends(request):
    """Piyasa trend analizi API endpoint'i"""
    try:
        service = FinancialAIService()
        trends = service.predict_market_trends(request.user, request.data)
        return Response(trends)
    except Exception as e:
        logger.error(f"Piyasa trend analizi hatası: {str(e)}")
        return Response(
            {"error": "Trend analizi sırasında bir hata oluştu."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def chat_with_ai(request):
    """AI sohbet API endpoint'i"""
    try:
        service = ChatAIService()
        response = await service.get_response(request.user, request.data.get('query', ''))
        return Response({"response": response})
    except Exception as e:
        logger.error(f"Sohbet yanıtı oluşturma hatası: {str(e)}")
        return Response(
            {"error": "Yanıt oluşturulurken bir hata oluştu."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """AI geri bildirimi API endpoint'i"""
    try:
        from .models import AIFeedback, AIModel
        
        model = AIModel.objects.get(id=request.data.get('model_id'))
        feedback = AIFeedback.objects.create(
            user=request.user,
            model=model,
            rating=request.data.get('rating'),
            comment=request.data.get('comment', '')
        )
        return Response({"message": "Geri bildiriminiz için teşekkürler!"})
    except Exception as e:
        logger.error(f"Geri bildirim kaydetme hatası: {str(e)}")
        return Response(
            {"error": "Geri bildirim kaydedilirken bir hata oluştu."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
