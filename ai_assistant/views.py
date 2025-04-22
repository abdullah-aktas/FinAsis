from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .services import FinancialAIService, ChatAIService
from .models.cashflow_forecaster import CashFlowForecaster
from .models.risk_scorer import CustomerRiskScorer
from .services.ocr_service import OCRService
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    UserInteraction, FinancialPrediction, FinancialReport,
    AnomalyDetection, TrendAnalysis, Recommendation, Notification
)
from .services import get_market_analysis

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
def recommendations_view(request):
    # Kullanıcının önerilerini al
    recommendations = Recommendation.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-created_at')[:5]

    # Piyasa analizini al
    market_analysis = get_market_analysis()

    # Kullanıcının bildirimlerini al
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'recommendations': recommendations,
        'market_analysis': market_analysis,
        'notifications': notifications
    }

    return render(request, 'ai_assistant/recommendations.html', context)

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

# Nakit Akışı Tahmini
@login_required
def forecast_view(request):
    """
    Nakit akışı tahmini görünümü
    """
    return render(request, 'ai_assistant/forecast_dashboard.html')

@login_required
def forecast_api(request):
    """
    Nakit akışı tahmini API endpoint'i
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            model_type = data.get('model_type', 'prophet')
            periods = int(data.get('periods', 90))
            
            # Geçmiş verileri al (örnek)
            historical_data = {
                'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'cash_in': [1000, 1500, 1200],
                'cash_out': [800, 1000, 900]
            }
            
            # Modeli oluştur ve eğit
            forecaster = CashFlowForecaster(model_type=model_type)
            forecaster.train(historical_data)
            
            # Tahmin yap
            forecast_results = forecaster.forecast(periods=periods)
            
            # Grafik oluştur
            fig = forecaster.plot_forecast(forecast_results)
            
            return JsonResponse({
                'success': True,
                'forecast': forecast_results,
                'plot': fig.to_json()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Risk Skorlama
@login_required
def risk_score_view(request, customer_id):
    """
    Müşteri risk skoru görünümü
    """
    try:
        # Müşteri verilerini al (örnek)
        customer_data = {
            'payment_delay_avg': 5,
            'payment_delay_count': 2,
            'transaction_amount_avg': 2500,
            'transaction_count': 10,
            'days_since_last_payment': 15,
            'sector_risk_score': 0.3
        }
        
        # Risk skorunu hesapla
        risk_scorer = CustomerRiskScorer()
        risk_score = risk_scorer.predict_risk_score(customer_data)
        
        return render(request, 'ai_assistant/risk_score.html', {
            'customer_id': customer_id,
            'risk_score': risk_score
        })
        
    except Exception as e:
        return render(request, 'ai_assistant/error.html', {
            'error_message': str(e)
        })

@login_required
def risk_score_api(request, customer_id):
    """
    Müşteri risk skoru API endpoint'i
    """
    try:
        # Müşteri verilerini al (örnek)
        customer_data = {
            'payment_delay_avg': 5,
            'payment_delay_count': 2,
            'transaction_amount_avg': 2500,
            'transaction_count': 10,
            'days_since_last_payment': 15,
            'sector_risk_score': 0.3
        }
        
        # Risk skorunu hesapla
        risk_scorer = CustomerRiskScorer()
        risk_score = risk_scorer.predict_risk_score(customer_data)
        
        return JsonResponse({
            'success': True,
            'risk_score': risk_score
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# OCR İşlemleri
@login_required
def ocr_upload_view(request):
    """
    OCR yükleme görünümü
    """
    return render(request, 'ai_assistant/ocr_upload.html')

@csrf_exempt
@login_required
def ocr_process_api(request):
    """
    OCR işleme API endpoint'i
    """
    if request.method == 'POST':
        try:
            # Dosyayı al
            file = request.FILES.get('file')
            if not file:
                return JsonResponse({
                    'success': False,
                    'error': 'Dosya yüklenmedi'
                })
                
            # Dosyayı kaydet
            file_path = default_storage.save(
                f'ocr_uploads/{file.name}',
                ContentFile(file.read())
            )
            
            # OCR işlemi
            ocr_service = OCRService()
            result = ocr_service.process_invoice(file_path)
            
            # Dosyayı sil
            default_storage.delete(file_path)
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# UserInteraction Views
class UserInteractionListView(LoginRequiredMixin, ListView):
    model = UserInteraction
    template_name = 'ai_assistant/userinteraction_list.html'
    context_object_name = 'interactions'

class UserInteractionDetailView(LoginRequiredMixin, DetailView):
    model = UserInteraction
    template_name = 'ai_assistant/userinteraction_detail.html'

class UserInteractionCreateView(LoginRequiredMixin, CreateView):
    model = UserInteraction
    template_name = 'ai_assistant/userinteraction_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:userinteraction_list')

class UserInteractionUpdateView(LoginRequiredMixin, UpdateView):
    model = UserInteraction
    template_name = 'ai_assistant/userinteraction_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:userinteraction_list')

class UserInteractionDeleteView(LoginRequiredMixin, DeleteView):
    model = UserInteraction
    template_name = 'ai_assistant/userinteraction_confirm_delete.html'
    success_url = reverse_lazy('ai_assistant:userinteraction_list')

# FinancialPrediction Views
class FinancialPredictionListView(LoginRequiredMixin, ListView):
    model = FinancialPrediction
    template_name = 'ai_assistant/financialprediction_list.html'
    context_object_name = 'predictions'

class FinancialPredictionDetailView(LoginRequiredMixin, DetailView):
    model = FinancialPrediction
    template_name = 'ai_assistant/financialprediction_detail.html'

class FinancialPredictionCreateView(LoginRequiredMixin, CreateView):
    model = FinancialPrediction
    template_name = 'ai_assistant/financialprediction_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:financialprediction_list')

class FinancialPredictionUpdateView(LoginRequiredMixin, UpdateView):
    model = FinancialPrediction
    template_name = 'ai_assistant/financialprediction_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:financialprediction_list')

class FinancialPredictionDeleteView(LoginRequiredMixin, DeleteView):
    model = FinancialPrediction
    template_name = 'ai_assistant/financialprediction_confirm_delete.html'
    success_url = reverse_lazy('ai_assistant:financialprediction_list')

# FinancialReport Views
class FinancialReportListView(LoginRequiredMixin, ListView):
    model = FinancialReport
    template_name = 'ai_assistant/financialreport_list.html'
    context_object_name = 'reports'

class FinancialReportDetailView(LoginRequiredMixin, DetailView):
    model = FinancialReport
    template_name = 'ai_assistant/financialreport_detail.html'

class FinancialReportCreateView(LoginRequiredMixin, CreateView):
    model = FinancialReport
    template_name = 'ai_assistant/financialreport_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:financialreport_list')

class FinancialReportUpdateView(LoginRequiredMixin, UpdateView):
    model = FinancialReport
    template_name = 'ai_assistant/financialreport_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:financialreport_list')

class FinancialReportDeleteView(LoginRequiredMixin, DeleteView):
    model = FinancialReport
    template_name = 'ai_assistant/financialreport_confirm_delete.html'
    success_url = reverse_lazy('ai_assistant:financialreport_list')

# AnomalyDetection Views
class AnomalyDetectionListView(LoginRequiredMixin, ListView):
    model = AnomalyDetection
    template_name = 'ai_assistant/anomalydetection_list.html'
    context_object_name = 'anomalies'

class AnomalyDetectionDetailView(LoginRequiredMixin, DetailView):
    model = AnomalyDetection
    template_name = 'ai_assistant/anomalydetection_detail.html'

class AnomalyDetectionCreateView(LoginRequiredMixin, CreateView):
    model = AnomalyDetection
    template_name = 'ai_assistant/anomalydetection_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:anomalydetection_list')

class AnomalyDetectionUpdateView(LoginRequiredMixin, UpdateView):
    model = AnomalyDetection
    template_name = 'ai_assistant/anomalydetection_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:anomalydetection_list')

class AnomalyDetectionDeleteView(LoginRequiredMixin, DeleteView):
    model = AnomalyDetection
    template_name = 'ai_assistant/anomalydetection_confirm_delete.html'
    success_url = reverse_lazy('ai_assistant:anomalydetection_list')

# TrendAnalysis Views
class TrendAnalysisListView(LoginRequiredMixin, ListView):
    model = TrendAnalysis
    template_name = 'ai_assistant/trendanalysis_list.html'
    context_object_name = 'trends'

class TrendAnalysisDetailView(LoginRequiredMixin, DetailView):
    model = TrendAnalysis
    template_name = 'ai_assistant/trendanalysis_detail.html'

class TrendAnalysisCreateView(LoginRequiredMixin, CreateView):
    model = TrendAnalysis
    template_name = 'ai_assistant/trendanalysis_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:trendanalysis_list')

class TrendAnalysisUpdateView(LoginRequiredMixin, UpdateView):
    model = TrendAnalysis
    template_name = 'ai_assistant/trendanalysis_form.html'
    fields = '__all__'
    success_url = reverse_lazy('ai_assistant:trendanalysis_list')

class TrendAnalysisDeleteView(LoginRequiredMixin, DeleteView):
    model = TrendAnalysis
    template_name = 'ai_assistant/trendanalysis_confirm_delete.html'
    success_url = reverse_lazy('ai_assistant:trendanalysis_list')
