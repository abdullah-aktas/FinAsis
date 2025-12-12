from django.shortcuts import render

# DİKKAT: Bu dizinde hem 'views.py' dosyası hem de 'views/' klasörü var!
# Python import sırasında çakışma yaşanabilir. Eğer 'from . import views' gibi bir import varsa,
# Python hangisini seçeceğini şaşırabilir. Bu durumda, ya 'views.py' dosyasını ya da 'views/' klasörünü yeniden adlandırın.
# Öneri: 'views/' klasörünü örneğin 'views_extra/' olarak değiştirin ve importları güncelleyin.
#
# Bu not, AttributeError: module 'views' has no attribute 'risk_score_api' hatasını önlemek içindir.
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
import json
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .services.financial_service import FinancialAIService
from .services.chat_service import ChatAIService
from .models import (
    CashFlowForecaster,
    CustomerRiskScorer,
    AIModel,
    UserInteraction,
    FinancialPrediction,
    AIFeedback,
    FinancialReport,
    AnomalyDetection,
    TrendAnalysis,
    UserPreference,
    AIInsight,
    Recommendation,
    Notification,
    MarketAnalysis,
)
from .services.ocr_service import OCRService
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .services.market_service import get_market_analysis
from .serializers import (
    AIModelSerializer,
    UserInteractionSerializer,
    FinancialPredictionSerializer,
    AIFeedbackSerializer,
    FinancialReportSerializer,
    AnomalyDetectionSerializer,
    TrendAnalysisSerializer,
    UserPreferenceSerializer,
    AIInsightSerializer,
    RecommendationSerializer,
    NotificationSerializer,
    MarketAnalysisSerializer,
)
from django.utils.translation import gettext_lazy as _
from rest_framework.renderers import JSONRenderer
from .services.ml_service import (
    RiskScoringService,
    FinancialForecastService,
    RecommendationService,
)
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@login_required
def ai_home(request):
    """AI asistanı ana sayfası"""
    return render(request, "ai_assistant/home.html")


@login_required
def ai_chat(request):
    """AI sohbet sayfası"""
    return render(request, "ai_assistant/chat.html")


@login_required
def voice_demo_view(request):
    """Mikrofon ile ses kaydı alıp API'ye gönderen basit demo sayfası."""
    return render(request, "ai_assistant/voice.html")


@login_required
def assistant_voucher_view(request):
    """Metin, ses veya belge ile fiş kesimi için birleşik asistan sayfası."""
    return render(request, "ai_assistant/assistant_voucher.html")


@login_required
def financial_analysis(request):
    """Finansal analiz sayfası"""
    return render(request, "ai_assistant/analysis.html")


@login_required
def recommendations_view(request):
    # Kullanıcının önerilerini al
    recommendations = Recommendation.objects.filter(
        user=request.user, is_active=True
    ).order_by("-created_at")[:5]

    # Piyasa analizini al
    market_analysis = get_market_analysis()

    # Kullanıcının bildirimlerini al
    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).order_by("-created_at")[:5]

    context = {
        "recommendations": recommendations,
        "market_analysis": market_analysis,
        "notifications": notifications,
    }

    return render(request, "ai_assistant/recommendations.html", context)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def analyze_financial_data(request):
    try:
        data = json.loads(request.body)
        financial_service = FinancialAIService()
        result = financial_service.analyze_financial_data(request.user, data)

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Finansal veri analizi hatası: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_ai_recommendations(request):
    """Kişiselleştirilmiş öneriler API endpoint'i"""
    try:
        # FinancialAIService'ta bu method yok; RecommendationService kullan
        rec_service = RecommendationService()
        recommendations = rec_service.generate(request.data)
        return Response({"recommendations": recommendations})
    except Exception as e:
        logger.error(f"Öneri oluşturma hatası: {str(e)}")
        return Response(
            {"error": "Öneriler oluşturulurken bir hata oluştu."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def predict_market_trends(request):
    """Piyasa trend analizi API endpoint'i"""
    try:
        # FinancialAIService'ta predict_market_trends yok; MarketAnalysis üzerinden sağla
        analysis = get_market_analysis()
        return Response({"analysis": analysis})
    except Exception as e:
        logger.error(f"Piyasa trend analizi hatası: {str(e)}")
        return Response(
            {"error": "Trend analizi sırasında bir hata oluştu."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_with_ai(request):
    try:
        data = json.loads(request.body)
        query = data.get("query")

        if not query:
            return Response(
                {"error": "Sorgu boş olamaz"}, status=status.HTTP_400_BAD_REQUEST
            )

        chat_service = ChatAIService()
        response = chat_service.get_response(request.user, query)

        return Response({"response": response}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"AI sohbet hatası: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """AI geri bildirimi API endpoint'i"""
    try:
        from .models import AIFeedback, AIModel

        model = AIModel.objects.get(id=request.data.get("model_id"))
        AIFeedback.objects.create(
            user=request.user,
            model=model,
            rating=request.data.get("rating"),
            comment=request.data.get("comment", ""),
        )
        return Response({"message": "Geri bildiriminiz için teşekkürler!"})
    except Exception as e:
        logger.error(f"Geri bildirim kaydetme hatası: {str(e)}")
        return Response(
            {"error": "Geri bildirim kaydedilirken bir hata oluştu."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Nakit Akışı Tahmini
@login_required
def forecast_view(request):
    """
    Nakit akışı tahmini görünümü
    """
    return render(request, "ai_assistant/forecast_dashboard.html")


@login_required
def forecast_api(request):
    """
    Nakit akışı tahmini API endpoint'i
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            model_type = data.get("model_type", "prophet")
            periods = int(data.get("periods", 90))

            # Geçmiş verileri al (örnek)
            historical_data = {
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "cash_in": [1000, 1500, 1200],
                "cash_out": [800, 1000, 900],
            }

            # Modeli oluştur ve eğit
            forecaster = CashFlowForecaster(model_type=model_type)
            forecaster.train(historical_data)

            # Tahmin yap
            forecast_results = forecaster.forecast(periods=periods)

            # Grafik oluştur
            fig = forecaster.plot_forecast(forecast_results)

            return JsonResponse(
                {"success": True, "forecast": forecast_results, "plot": fig.to_json()}
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"error": "Method not allowed"}, status=405)


# Risk Skorlama
@login_required
def risk_score_view(request, customer_id):
    """
    Müşteri risk skoru görünümü
    """
    try:
        # Müşteri verilerini al (örnek)
        customer_data = {
            "payment_delay_avg": 5,
            "payment_delay_count": 2,
            "transaction_amount_avg": 2500,
            "transaction_count": 10,
            "days_since_last_payment": 15,
            "sector_risk_score": 0.3,
        }

        # Risk skorunu hesapla
        risk_scorer = CustomerRiskScorer()
        risk_score = risk_scorer.predict_risk_score(customer_data)

        return render(
            request,
            "ai_assistant/risk_score.html",
            {"customer_id": customer_id, "risk_score": risk_score},
        )

    except Exception as e:
        return render(request, "ai_assistant/error.html", {"error_message": str(e)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def risk_score_api(request):
    """
    Müşteri risk skorunu hesaplar.
    Beklenen veri: {
        "features": [float, ...]  # Modelin beklediği sırada feature listesi
    }
    """
    try:
        features = request.data.get("features")
        if not features or not isinstance(features, list):
            return Response(
                {"error": _("Geçerli bir feature listesi giriniz.")}, status=400
            )
        features_np = np.array(features, dtype=float)
        service = RiskScoringService()
        result = service.predict(features_np, user=request.user)
        UserInteraction.objects.create(
            user=request.user,
            interaction_type="analysis",
            content=str(features),
            ai_response=str(result),
            processing_time=0.0,
        )
        return Response(result)
    except Exception as e:
        return Response(
            {"error": _("Risk skoru hesaplanırken hata oluştu: ") + str(e)}, status=500
        )


# OCR İşlemleri
@login_required
def ocr_upload_view(request):
    """
    OCR yükleme görünümü
    """
    return render(request, "ai_assistant/ocr_upload.html")


@login_required
def ocr_process_api(request):
    """
    OCR işleme API endpoint'i
    """
    if request.method == "POST":
        try:
            # Dosyayı al
            file = request.FILES.get("file")
            if not file:
                return JsonResponse({"success": False, "error": "Dosya yüklenmedi"})

            # Dosyayı kaydet
            file_path = default_storage.save(
                f"ocr_uploads/{file.name}", ContentFile(file.read())
            )

            # OCR işlemi
            ocr_service = OCRService()
            result = ocr_service.process_invoice(file_path)

            # Dosyayı sil
            default_storage.delete(file_path)

            # Hata anahtarı varsa başarısız say
            if isinstance(result, dict) and result.get("error"):
                return JsonResponse({"success": False, "error": result.get("error")})
            # Frontend beklenen şema: { success: True, data: {...} }
            return JsonResponse({"success": True, "data": result})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"error": "Method not allowed"}, status=405)


# UserInteraction Views
class UserInteractionListView(LoginRequiredMixin, ListView):
    model = UserInteraction
    template_name = "ai_assistant/userinteraction_list.html"
    context_object_name = "interactions"


class UserInteractionDetailView(LoginRequiredMixin, DetailView):
    model = UserInteraction
    template_name = "ai_assistant/userinteraction_detail.html"


class UserInteractionCreateView(LoginRequiredMixin, CreateView):
    model = UserInteraction
    template_name = "ai_assistant/userinteraction_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:userinteraction_list")


class UserInteractionUpdateView(LoginRequiredMixin, UpdateView):
    model = UserInteraction
    template_name = "ai_assistant/userinteraction_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:userinteraction_list")


class UserInteractionDeleteView(LoginRequiredMixin, DeleteView):
    model = UserInteraction
    template_name = "ai_assistant/userinteraction_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:userinteraction_list")


# FinancialPrediction Views
class FinancialPredictionListView(LoginRequiredMixin, ListView):
    model = FinancialPrediction
    template_name = "ai_assistant/financialprediction_list.html"
    context_object_name = "predictions"


class FinancialPredictionDetailView(LoginRequiredMixin, DetailView):
    model = FinancialPrediction
    template_name = "ai_assistant/financialprediction_detail.html"


class FinancialPredictionCreateView(LoginRequiredMixin, CreateView):
    model = FinancialPrediction
    template_name = "ai_assistant/financialprediction_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:financialprediction_list")


class FinancialPredictionUpdateView(LoginRequiredMixin, UpdateView):
    model = FinancialPrediction
    template_name = "ai_assistant/financialprediction_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:financialprediction_list")


class FinancialPredictionDeleteView(LoginRequiredMixin, DeleteView):
    model = FinancialPrediction
    template_name = "ai_assistant/financialprediction_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:financialprediction_list")


# FinancialReport Views
class FinancialReportListView(LoginRequiredMixin, ListView):
    model = FinancialReport
    template_name = "ai_assistant/financialreport_list.html"
    context_object_name = "reports"


class FinancialReportDetailView(LoginRequiredMixin, DetailView):
    model = FinancialReport
    template_name = "ai_assistant/financialreport_detail.html"


class FinancialReportCreateView(LoginRequiredMixin, CreateView):
    model = FinancialReport
    template_name = "ai_assistant/financialreport_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:financialreport_list")


class FinancialReportUpdateView(LoginRequiredMixin, UpdateView):
    model = FinancialReport
    template_name = "ai_assistant/financialreport_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:financialreport_list")


class FinancialReportDeleteView(LoginRequiredMixin, DeleteView):
    model = FinancialReport
    template_name = "ai_assistant/financialreport_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:financialreport_list")


# AnomalyDetection Views
class AnomalyDetectionListView(LoginRequiredMixin, ListView):
    model = AnomalyDetection
    template_name = "ai_assistant/anomalydetection_list.html"
    context_object_name = "anomalies"


class AnomalyDetectionDetailView(LoginRequiredMixin, DetailView):
    model = AnomalyDetection
    template_name = "ai_assistant/anomalydetection_detail.html"


class AnomalyDetectionCreateView(LoginRequiredMixin, CreateView):
    model = AnomalyDetection
    template_name = "ai_assistant/anomalydetection_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:anomalydetection_list")


class AnomalyDetectionUpdateView(LoginRequiredMixin, UpdateView):
    model = AnomalyDetection
    template_name = "ai_assistant/anomalydetection_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:anomalydetection_list")


class AnomalyDetectionDeleteView(LoginRequiredMixin, DeleteView):
    model = AnomalyDetection
    template_name = "ai_assistant/anomalydetection_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:anomalydetection_list")


# TrendAnalysis Views
class TrendAnalysisListView(LoginRequiredMixin, ListView):
    model = TrendAnalysis
    template_name = "ai_assistant/trendanalysis_list.html"
    context_object_name = "trends"


class TrendAnalysisDetailView(LoginRequiredMixin, DetailView):
    model = TrendAnalysis
    template_name = "ai_assistant/trendanalysis_detail.html"


class TrendAnalysisCreateView(LoginRequiredMixin, CreateView):
    model = TrendAnalysis
    template_name = "ai_assistant/trendanalysis_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:trendanalysis_list")


class TrendAnalysisUpdateView(LoginRequiredMixin, UpdateView):
    model = TrendAnalysis
    template_name = "ai_assistant/trendanalysis_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:trendanalysis_list")


class TrendAnalysisDeleteView(LoginRequiredMixin, DeleteView):
    model = TrendAnalysis
    template_name = "ai_assistant/trendanalysis_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:trendanalysis_list")


class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]


class UserInteractionViewSet(viewsets.ModelViewSet):
    queryset = UserInteraction.objects.all()
    serializer_class = UserInteractionSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class FinancialPredictionViewSet(viewsets.ModelViewSet):
    queryset = FinancialPrediction.objects.all()
    serializer_class = FinancialPredictionSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class AIFeedbackViewSet(viewsets.ModelViewSet):
    queryset = AIFeedback.objects.all()
    serializer_class = AIFeedbackSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class FinancialReportViewSet(viewsets.ModelViewSet):
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]


class AnomalyDetectionViewSet(viewsets.ModelViewSet):
    queryset = AnomalyDetection.objects.all()
    serializer_class = AnomalyDetectionSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]


class TrendAnalysisViewSet(viewsets.ModelViewSet):
    queryset = TrendAnalysis.objects.all()
    serializer_class = TrendAnalysisSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]


class UserPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class AIInsightViewSet(viewsets.ModelViewSet):
    queryset = AIInsight.objects.all()
    serializer_class = AIInsightSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class MarketAnalysisViewSet(viewsets.ModelViewSet):
    queryset = MarketAnalysis.objects.all()
    serializer_class = MarketAnalysisSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    @action(detail=False, methods=["get"])
    def latest(self):
        latest_analysis = self.get_queryset().order_by("-timestamp").first()
        serializer = self.get_serializer(latest_analysis)
        return Response(serializer.data)


class ChatViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            chat_service = ChatAIService()
            response = chat_service.get_response(
                request.user, request.data.get("query")
            )
            return Response({"response": response}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return Response(
                {"error": _("Sohbet işlemi sırasında bir hata oluştu.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FinancialAnalysisViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            financial_service = FinancialAIService()
            analysis = financial_service.analyze_financial_data(
                request.user, request.data
            )
            return Response(analysis, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Financial analysis error: {str(e)}")
            return Response(
                {"error": _("Finansal analiz sırasında bir hata oluştu.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OCRViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def create(self, request):
        try:
            ocr_service = OCRService()
            result = ocr_service.process_invoice(request.FILES.get("image"))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            return Response(
                {"error": _("OCR işlemi sırasında bir hata oluştu.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_assistant_chat(request):
    """
    Kullanıcıdan gelen mesajı AI asistanına iletir ve yanıtı döner.
    """
    try:
        # Request data'yı al - hem JSON hem form data destekle
        try:
            if hasattr(request, 'data'):
                data = request.data
            else:
                data = json.loads(request.body) if request.body else {}
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Request data parse hatası: {e}")
            data = {}
        
        message = data.get("message") or data.get("query") or ""
        context = data.get("context") or {
            "page_path": request.headers.get("X-Page-Path")
            or request.META.get("HTTP_REFERER", ""),
            "page_title": request.headers.get("X-Page-Title", ""),
            "locale": (
                request.LANGUAGE_CODE if hasattr(request, "LANGUAGE_CODE") else None
            ),
        }
        
        if not message or not message.strip():
            return Response(
                {"error": "Mesaj boş olamaz."}, status=status.HTTP_400_BAD_REQUEST
            )
        
        # Chat servisini başlat ve yanıt al
        try:
            chat_service = ChatAIService()
            response_text = chat_service.get_response(
                request.user, message.strip(), context=context
            )
            
            if not response_text:
                response_text = "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."
        except Exception as service_err:
            logger.error(f"ChatAIService hatası: {service_err}", exc_info=True)
            response_text = "AI servisi şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin."

        # Etkileşimi kaydet (model alanı opsiyonel; şema gerektirmiyor)
        try:
            UserInteraction.objects.create(
                user=request.user,
                interaction_type="chat",
                content=message.strip(),
                ai_response=response_text,
                processing_time=0.0,
            )
        except Exception as e:
            logger.warning(f"UserInteraction kaydı başarısız: {e}")

        return Response({"response": response_text}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"AI asistan chat endpoint hatası: {str(e)}", exc_info=True)
        error_msg = "Bir hata oluştu. Lütfen daha sonra tekrar deneyin."
        # Production'da detaylı hata mesajı gösterme
        if settings.DEBUG:
            error_msg = f"Hata: {str(e)}"
        return Response({"error": error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIModelListView(ListView):
    model = AIModel
    template_name = "ai_assistant/a_i_model_list.html"
    context_object_name = "object_list"


class AIModelDetailView(DetailView):
    model = AIModel
    template_name = "ai_assistant/a_i_model_detail.html"
    context_object_name = "object"


class AIModelCreateView(CreateView):
    model = AIModel
    template_name = "ai_assistant/a_i_model_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:a_i_model_list")


class AIModelUpdateView(UpdateView):
    model = AIModel
    template_name = "ai_assistant/a_i_model_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:a_i_model_list")


class AIModelDeleteView(DeleteView):
    model = AIModel
    template_name = "ai_assistant/a_i_model_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:a_i_model_list")


class AIFeedbackListView(ListView):
    model = AIFeedback
    template_name = "ai_assistant/a_i_feedback_list.html"
    context_object_name = "object_list"


class AIFeedbackDetailView(DetailView):
    model = AIFeedback
    template_name = "ai_assistant/a_i_feedback_detail.html"
    context_object_name = "object"


class AIFeedbackCreateView(CreateView):
    model = AIFeedback
    template_name = "ai_assistant/a_i_feedback_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:a_i_feedback_list")


class AIFeedbackUpdateView(UpdateView):
    model = AIFeedback
    template_name = "ai_assistant/a_i_feedback_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:a_i_feedback_list")


class AIFeedbackDeleteView(DeleteView):
    model = AIFeedback
    template_name = "ai_assistant/a_i_feedback_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:a_i_feedback_list")


class UserPreferenceListView(LoginRequiredMixin, ListView):
    model = UserPreference
    template_name = "ai_assistant/user_preference_list.html"
    context_object_name = "object_list"


class UserPreferenceDetailView(LoginRequiredMixin, DetailView):
    model = UserPreference
    template_name = "ai_assistant/user_preference_detail.html"
    context_object_name = "object"


class UserPreferenceCreateView(LoginRequiredMixin, CreateView):
    model = UserPreference
    template_name = "ai_assistant/user_preference_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:user_preference_list")


class UserPreferenceUpdateView(LoginRequiredMixin, UpdateView):
    model = UserPreference
    template_name = "ai_assistant/user_preference_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:user_preference_list")


class UserPreferenceDeleteView(LoginRequiredMixin, DeleteView):
    model = UserPreference
    template_name = "ai_assistant/user_preference_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:user_preference_list")


class AIInsightListView(LoginRequiredMixin, ListView):
    model = AIInsight
    template_name = "ai_assistant/a_i_insight_list.html"
    context_object_name = "object_list"


class AIInsightDetailView(LoginRequiredMixin, DetailView):
    model = AIInsight
    template_name = "ai_assistant/a_i_insight_detail.html"
    context_object_name = "object"


class AIInsightCreateView(LoginRequiredMixin, CreateView):
    model = AIInsight
    template_name = "ai_assistant/a_i_insight_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:a_i_insight_list")


class AIInsightUpdateView(LoginRequiredMixin, UpdateView):
    model = AIInsight
    template_name = "ai_assistant/a_i_insight_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:a_i_insight_list")


class AIInsightDeleteView(LoginRequiredMixin, DeleteView):
    model = AIInsight
    template_name = "ai_assistant/a_i_insight_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:a_i_insight_list")


class RecommendationListView(LoginRequiredMixin, ListView):
    model = Recommendation
    template_name = "ai_assistant/recommendation_list.html"
    context_object_name = "object_list"


class RecommendationDetailView(LoginRequiredMixin, DetailView):
    model = Recommendation
    template_name = "ai_assistant/recommendation_detail.html"
    context_object_name = "object"


class RecommendationCreateView(LoginRequiredMixin, CreateView):
    model = Recommendation
    template_name = "ai_assistant/recommendation_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:recommendation_list")


class RecommendationUpdateView(LoginRequiredMixin, UpdateView):
    model = Recommendation
    template_name = "ai_assistant/recommendation_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:recommendation_list")


class RecommendationDeleteView(LoginRequiredMixin, DeleteView):
    model = Recommendation
    template_name = "ai_assistant/recommendation_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:recommendation_list")


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "ai_assistant/notification_list.html"
    context_object_name = "object_list"


class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = Notification
    template_name = "ai_assistant/notification_detail.html"
    context_object_name = "object"


class NotificationCreateView(LoginRequiredMixin, CreateView):
    model = Notification
    template_name = "ai_assistant/notification_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:notification_list")


class NotificationUpdateView(LoginRequiredMixin, UpdateView):
    model = Notification
    template_name = "ai_assistant/notification_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:notification_list")


class NotificationDeleteView(LoginRequiredMixin, DeleteView):
    model = Notification
    template_name = "ai_assistant/notification_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:notification_list")


class MarketAnalysisListView(LoginRequiredMixin, ListView):
    model = MarketAnalysis
    template_name = "ai_assistant/market_analysis_list.html"
    context_object_name = "object_list"


class MarketAnalysisDetailView(LoginRequiredMixin, DetailView):
    model = MarketAnalysis
    template_name = "ai_assistant/market_analysis_detail.html"
    context_object_name = "object"


class MarketAnalysisCreateView(LoginRequiredMixin, CreateView):
    model = MarketAnalysis
    template_name = "ai_assistant/market_analysis_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:market_analysis_list")


class MarketAnalysisUpdateView(LoginRequiredMixin, UpdateView):
    model = MarketAnalysis
    template_name = "ai_assistant/market_analysis_form.html"
    fields = "__all__"
    success_url = reverse_lazy("ai_assistant:market_analysis_list")


class MarketAnalysisDeleteView(LoginRequiredMixin, DeleteView):
    model = MarketAnalysis
    template_name = "ai_assistant/market_analysis_confirm_delete.html"
    success_url = reverse_lazy("ai_assistant:market_analysis_list")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def financial_forecast_api(request):
    """
    Finansal tahmin (Prophet) API.
    Beklenen veri: {
        "history": [{"ds": "2024-01-01", "y": 123.0}, ...],
        "periods": 90
    }
    """
    try:
        data = request.data.get("data")
        periods = int(request.data.get("periods", 90))
        if not data or not isinstance(data, list):
            return Response({"error": _("Geçerli veri listesi giriniz.")}, status=400)
        df = pd.DataFrame(data)
        if "ds" not in df or "y" not in df:
            return Response(
                {"error": _("Veri formatı yanlış. ds ve y sütunları olmalı.")},
                status=400,
            )
        service = FinancialForecastService()
        service.train(df, user=request.user)
        result = service.forecast(periods, user=request.user)
        UserInteraction.objects.create(
            user=request.user,
            interaction_type="analysis",
            content=str(data),
            ai_response=str(result),
            processing_time=0.0,
        )
        return Response(result)
    except Exception as e:
        return Response(
            {"error": _("Tahmin yapılırken hata oluştu: ") + str(e)}, status=500
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recommendation_api(request):
    """
    Finansal öneri API.
    Beklenen veri: {
        "income": float,
        "expenses": float,
        "savings": float,
        "goals": str
    }
    """
    try:
        data = request.data
        service = RecommendationService()
        context = {
            "page_path": request.headers.get("X-Page-Path")
            or request.META.get("HTTP_REFERER"),
            "page_title": request.headers.get("X-Page-Title"),
        }
        result = service.generate(data, user=request.user, context=context)
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


def home(request):
    return render(request, "ai_assistant/home.html")


# Basit sağlık kontrolü: AI istemcisi/mode durumu
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def ai_health(request):
    try:
        svc = ChatAIService()
        status_info = {
            "ok": True,
            "mock_mode": bool(getattr(svc, "mock_mode", False)),
            "client_initialized": bool(getattr(svc, "client", None)),
            "model": os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        }
        return Response(status_info, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"ok": False, "error": str(e)}, status=status.HTTP_200_OK)
