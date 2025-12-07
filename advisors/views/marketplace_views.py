# -*- coding: utf-8 -*-
"""
Mali Müşavir Marketplace API Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.utils import timezone
from decimal import Decimal

from ..models_marketplace import (
    ConsultantProfile,
    ConsultantService,
    ConsultationBooking,
    ConsultationPayment,
    ConsultantContract,
    ConsultantReview,
    ConsultantAvailability,
)
from ..serializers.marketplace_serializers import (
    ConsultantProfileListSerializer,
    ConsultantProfileDetailSerializer,
    ConsultantProfileCreateSerializer,
    ConsultantServiceSerializer,
    ConsultationBookingSerializer,
    ConsultationBookingUpdateSerializer,
    ConsultationPaymentSerializer,
    ConsultantContractSerializer,
    ConsultantReviewSerializer,
    ConsultantAvailabilitySerializer,
    ConsultantDashboardSerializer,
    ClientDashboardSerializer,
)


class ConsultantProfileViewSet(viewsets.ModelViewSet):
    """
    Mali Müşavir Profilleri ViewSet

    list: Tüm mali müşavirleri listele (filtreleme ve arama destekli)
    retrieve: Mali müşavir detaylarını getir
    create: Yeni mali müşavir profili oluştur
    update: Mali müşavir profilini güncelle
    partial_update: Mali müşavir profilini kısmi güncelle
    """

    queryset = ConsultantProfile.objects.filter(approval_status="approved")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["city", "availability_status", "is_featured"]
    search_fields = ["display_name", "bio", "specializations"]
    ordering_fields = [
        "average_rating",
        "total_reviews",
        "hourly_rate",
        "years_of_experience",
    ]
    ordering = ["-is_featured", "-average_rating"]

    def get_serializer_class(self):
        if self.action == "list":
            return ConsultantProfileListSerializer
        elif self.action == "create":
            return ConsultantProfileCreateSerializer
        return ConsultantProfileDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Uzmanlık alanına göre filtrele
        specialization = self.request.query_params.get("specialization", None)
        if specialization:
            queryset = queryset.filter(specializations__contains=[specialization])

        # Fiyat aralığına göre filtrele
        min_rate = self.request.query_params.get("min_rate", None)
        max_rate = self.request.query_params.get("max_rate", None)
        if min_rate:
            queryset = queryset.filter(hourly_rate__gte=min_rate)
        if max_rate:
            queryset = queryset.filter(hourly_rate__lte=max_rate)

        # Sadece müsait olanlar
        available_only = self.request.query_params.get("available_only", None)
        if available_only == "true":
            queryset = queryset.filter(
                availability_status="available", accepts_new_clients=True
            )

        return queryset

    @action(detail=True, methods=["get"])
    def availability(self, request, pk=None):
        """Mali müşavirin müsaitlik takvimini getir"""
        consultant = self.get_object()
        slots = consultant.availability_slots.all()
        serializer = ConsultantAvailabilitySerializer(slots, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        """Mali müşavirin değerlendirmelerini getir"""
        consultant = self.get_object()
        reviews = consultant.reviews.filter(is_published=True).order_by("-created_at")

        # Pagination
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ConsultantReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ConsultantReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def services(self, request, pk=None):
        """Mali müşavirin hizmetlerini getir"""
        consultant = self.get_object()
        services = consultant.services.filter(is_active=True)
        serializer = ConsultantServiceSerializer(services, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def request_approval(self, request, pk=None):
        """Onay için başvur"""
        consultant = self.get_object()

        # Sadece kendi profilini onaya gönderebilir
        if consultant.advisor.user != request.user:
            return Response(
                {"error": "Sadece kendi profilinizi onaya gönderebilirsiniz."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if consultant.approval_status not in ["pending", "rejected"]:
            return Response(
                {"error": "Bu profil zaten onaylanmış veya inceleniyor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        consultant.approval_status = "under_review"
        consultant.save(update_fields=["approval_status"])

        return Response({"message": "Profiliniz onay için gönderildi."})

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Öne çıkan mali müşavirler"""
        consultants = self.get_queryset().filter(
            is_featured=True, featured_until__gte=timezone.now()
        )[:10]
        serializer = self.get_serializer(consultants, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def top_rated(self, request):
        """En yüksek puanlı mali müşavirler"""
        consultants = (
            self.get_queryset()
            .filter(total_reviews__gte=5)
            .order_by("-average_rating")[:10]
        )
        serializer = self.get_serializer(consultants, many=True)
        return Response(serializer.data)


class ConsultantServiceViewSet(viewsets.ModelViewSet):
    """
    Mali Müşavir Hizmetleri ViewSet
    """

    queryset = ConsultantService.objects.filter(is_active=True)
    serializer_class = ConsultantServiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "pricing_type", "consultant"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Mali müşavir kendi hizmetlerini görür
        if hasattr(self.request.user, "advisor_profile"):
            if hasattr(self.request.user.advisor_profile, "marketplace_profile"):
                consultant = self.request.user.advisor_profile.marketplace_profile
                queryset = queryset.filter(consultant=consultant)

        return queryset

    def perform_create(self, serializer):
        # Mali müşavir profilini al
        if self.request.user.is_authenticated and hasattr(
            self.request.user, "advisor_profile"
        ):
            consultant = self.request.user.advisor_profile.marketplace_profile
            serializer.save(consultant=consultant)


class ConsultationBookingViewSet(viewsets.ModelViewSet):
    """
    Danışmanlık Randevuları ViewSet
    """

    queryset = ConsultationBooking.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "meeting_type", "payment_status"]
    ordering_fields = ["scheduled_date", "created_at"]
    ordering = ["-scheduled_date"]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ConsultationBookingUpdateSerializer
        return ConsultationBookingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Müşteri kendi randevularını görür
        # Mali müşavir kendine ait randevuları görür
        if hasattr(user, "advisor_profile"):
            if hasattr(user.advisor_profile, "marketplace_profile"):
                consultant = user.advisor_profile.marketplace_profile
                queryset = queryset.filter(consultant=consultant)
        else:
            queryset = queryset.filter(client=user)

        return queryset

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """Randevuyu onayla (mali müşavir)"""
        booking = self.get_object()

        # Sadece mali müşavir onaylayabilir
        if booking.consultant.advisor.user != request.user:
            return Response(
                {"error": "Bu randevuyu onaylama yetkiniz yok."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status != "pending":
            return Response(
                {"error": "Bu randevu zaten onaylanmış veya iptal edilmiş."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.confirm()

        return Response(
            {
                "message": "Randevu onaylandı.",
                "booking": ConsultationBookingSerializer(booking).data,
            }
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Randevuyu tamamla"""
        booking = self.get_object()

        # Sadece mali müşavir tamamlayabilir
        if booking.consultant.advisor.user != request.user:
            return Response(
                {"error": "Bu randevuyu tamamlama yetkiniz yok."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status != "confirmed":
            return Response(
                {"error": "Sadece onaylanmış randevular tamamlanabilir."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Notları ekle
        consultant_notes = request.data.get("consultant_notes", "")
        if consultant_notes:
            booking.consultant_notes = consultant_notes

        booking.complete()

        return Response(
            {
                "message": "Randevu tamamlandı.",
                "booking": ConsultationBookingSerializer(booking).data,
            }
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Randevuyu iptal et"""
        booking = self.get_object()
        reason = request.data.get("reason", "")

        # Müşteri veya mali müşavir iptal edebilir
        if (
            booking.client != request.user
            and booking.consultant.advisor.user != request.user
        ):
            return Response(
                {"error": "Bu randevuyu iptal etme yetkiniz yok."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status in [
            "completed",
            "cancelled_by_client",
            "cancelled_by_consultant",
        ]:
            return Response(
                {"error": "Bu randevu zaten tamamlanmış veya iptal edilmiş."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Kim iptal ediyor?
        if booking.client == request.user:
            booking.status = "cancelled_by_client"
        else:
            booking.status = "cancelled_by_consultant"

        booking.cancellation_reason = reason
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=["status", "cancellation_reason", "cancelled_at"])

        # Online toplantıyı iptal et
        if booking.meeting_type == "online" and booking.meeting_id:
            booking.cancel_online_meeting()

        return Response(
            {
                "message": "Randevu iptal edildi.",
                "booking": ConsultationBookingSerializer(booking).data,
            }
        )

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Yaklaşan randevular"""
        today = timezone.now().date()
        bookings = (
            self.get_queryset()
            .filter(scheduled_date__gte=today, status__in=["pending", "confirmed"])
            .order_by("scheduled_date", "scheduled_time")[:10]
        )

        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def past(self, request):
        """Geçmiş randevular"""
        today = timezone.now().date()
        bookings = (
            self.get_queryset()
            .filter(Q(scheduled_date__lt=today) | Q(status="completed"))
            .order_by("-scheduled_date")
        )

        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)


class ConsultationPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Danışmanlık Ödemeleri ViewSet (Read-only)
    """

    queryset = ConsultationPayment.objects.all()
    serializer_class = ConsultationPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "payment_method", "payment_type"]
    ordering_fields = ["created_at", "paid_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Müşteri kendi ödemelerini görür
        # Mali müşavir kendine ait ödemeleri görür
        if hasattr(user, "advisor_profile"):
            if hasattr(user.advisor_profile, "marketplace_profile"):
                consultant = user.advisor_profile.marketplace_profile
                queryset = queryset.filter(consultant=consultant)
        else:
            queryset = queryset.filter(client=user)

        return queryset


class ConsultantContractViewSet(viewsets.ModelViewSet):
    """
    Mali Müşavir Sözleşmeleri ViewSet
    """

    queryset = ConsultantContract.objects.all()
    serializer_class = ConsultantContractSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "contract_type"]
    ordering_fields = ["created_at", "start_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Müşteri kendi sözleşmelerini görür
        # Mali müşavir kendine ait sözleşmeleri görür
        if hasattr(user, "advisor_profile"):
            if hasattr(user.advisor_profile, "marketplace_profile"):
                consultant = user.advisor_profile.marketplace_profile
                queryset = queryset.filter(consultant=consultant)
        else:
            queryset = queryset.filter(client=user)

        return queryset

    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        """Sözleşmeyi imzala"""
        contract = self.get_object()
        user = request.user

        # Müşteri veya mali müşavir imzalayabilir
        if contract.client == user:
            if contract.client_signed_at:
                return Response(
                    {"error": "Bu sözleşmeyi zaten imzaladınız."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            contract.client_signed_at = timezone.now()
            contract.client_ip = self.get_client_ip(request)
        elif hasattr(user, "advisor_profile"):
            if hasattr(user.advisor_profile, "marketplace_profile"):
                if contract.consultant == user.advisor_profile.marketplace_profile:
                    if contract.consultant_signed_at:
                        return Response(
                            {"error": "Bu sözleşmeyi zaten imzaladınız."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    contract.consultant_signed_at = timezone.now()
                    contract.consultant_ip = self.get_client_ip(request)
        else:
            return Response(
                {"error": "Bu sözleşmeyi imzalama yetkiniz yok."},
                status=status.HTTP_403_FORBIDDEN,
            )

        contract.save()

        # Her iki taraf da imzaladıysa aktifleştir
        if contract.is_fully_signed() and contract.status == "sent":
            contract.activate()

        return Response(
            {
                "message": "Sözleşme imzalandı.",
                "contract": ConsultantContractSerializer(contract).data,
            }
        )

    def get_client_ip(self, request):
        """İstemci IP adresini al"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class ConsultantReviewViewSet(viewsets.ModelViewSet):
    """
    Mali Müşavir Değerlendirmeleri ViewSet
    """

    queryset = ConsultantReview.objects.filter(is_published=True)
    serializer_class = ConsultantReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["consultant", "rating", "is_verified"]
    ordering_fields = ["created_at", "rating", "helpful_count"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def respond(self, request, pk=None):
        """Değerlendirmeye yanıt ver (mali müşavir)"""
        review = self.get_object()

        # Sadece ilgili mali müşavir yanıt verebilir
        if review.consultant.advisor.user != request.user:
            return Response(
                {"error": "Bu değerlendirmeye yanıt verme yetkiniz yok."},
                status=status.HTTP_403_FORBIDDEN,
            )

        response_text = request.data.get("response", "")
        if not response_text:
            return Response(
                {"error": "Yanıt metni gereklidir."}, status=status.HTTP_400_BAD_REQUEST
            )

        review.consultant_response = response_text
        review.consultant_responded_at = timezone.now()
        review.save(update_fields=["consultant_response", "consultant_responded_at"])

        return Response(
            {
                "message": "Yanıt eklendi.",
                "review": ConsultantReviewSerializer(review).data,
            }
        )

    @action(detail=True, methods=["post"])
    def mark_helpful(self, request, pk=None):
        """Değerlendirmeyi faydalı olarak işaretle"""
        review = self.get_object()
        review.helpful_count += 1
        review.save(update_fields=["helpful_count"])

        return Response({"message": "Teşekkürler!"})


class ConsultantAvailabilityViewSet(viewsets.ModelViewSet):
    """
    Mali Müşavir Müsaitlik ViewSet
    """

    queryset = ConsultantAvailability.objects.all()
    serializer_class = ConsultantAvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Sadece mali müşavir kendi müsaitliğini yönetir
        if hasattr(user, "advisor_profile"):
            if hasattr(user.advisor_profile, "marketplace_profile"):
                consultant = user.advisor_profile.marketplace_profile
                queryset = queryset.filter(consultant=consultant)

        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and hasattr(
            self.request.user, "advisor_profile"
        ):
            consultant = self.request.user.advisor_profile.marketplace_profile
            serializer.save(consultant=consultant)


class ConsultantDashboardView(viewsets.ViewSet):
    """
    Mali Müşavir Dashboard İstatistikleri
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Dashboard istatistikleri"""
        user = request.user

        if not hasattr(user, "advisor_profile"):
            return Response(
                {"error": "Mali müşavir profili bulunamadı."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not hasattr(user.advisor_profile, "marketplace_profile"):
            return Response(
                {"error": "Marketplace profili bulunamadı."},
                status=status.HTTP_404_NOT_FOUND,
            )

        consultant = user.advisor_profile.marketplace_profile

        # Kazanç istatistikleri
        total_earnings = consultant.total_earnings

        # Bekleyen kazançlar (ödenmemiş)
        pending_payments = ConsultationPayment.objects.filter(
            consultant=consultant,
            status="completed",
            payout_to_consultant_at__isnull=True,
        ).aggregate(total=Sum("consultant_amount"))
        pending_earnings = pending_payments["total"] or Decimal("0.00")

        # Bu ay kazanç
        this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        this_month_payments = ConsultationPayment.objects.filter(
            consultant=consultant, paid_at__gte=this_month_start
        ).aggregate(total=Sum("consultant_amount"))
        this_month_earnings = this_month_payments["total"] or Decimal("0.00")

        # Randevu istatistikleri
        total_consultations = consultant.total_consultations
        completed_consultations = consultant.completed_consultations

        upcoming_bookings = ConsultationBooking.objects.filter(
            consultant=consultant,
            scheduled_date__gte=timezone.now().date(),
            status__in=["pending", "confirmed"],
        ).count()

        pending_bookings = ConsultationBooking.objects.filter(
            consultant=consultant, status="pending"
        ).count()

        # Müşteri istatistikleri
        active_clients = (
            ConsultationBooking.objects.filter(
                consultant=consultant, status="confirmed"
            )
            .values("client")
            .distinct()
            .count()
        )

        total_clients = (
            ConsultationBooking.objects.filter(consultant=consultant)
            .values("client")
            .distinct()
            .count()
        )

        data = {
            "total_earnings": total_earnings,
            "pending_earnings": pending_earnings,
            "this_month_earnings": this_month_earnings,
            "total_consultations": total_consultations,
            "completed_consultations": completed_consultations,
            "upcoming_bookings": upcoming_bookings,
            "pending_bookings": pending_bookings,
            "average_rating": consultant.average_rating,
            "total_reviews": consultant.total_reviews,
            "active_clients": active_clients,
            "total_clients": total_clients,
        }

        serializer = ConsultantDashboardSerializer(data)
        return Response(serializer.data)


class ClientDashboardView(viewsets.ViewSet):
    """
    Müşteri Dashboard İstatistikleri
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Dashboard istatistikleri"""
        user = request.user

        # Randevu istatistikleri
        total_bookings = ConsultationBooking.objects.filter(client=user).count()
        completed_bookings = ConsultationBooking.objects.filter(
            client=user, status="completed"
        ).count()
        upcoming_bookings = ConsultationBooking.objects.filter(
            client=user,
            scheduled_date__gte=timezone.now().date(),
            status__in=["pending", "confirmed"],
        ).count()

        # Harcama istatistikleri
        total_payments = ConsultationPayment.objects.filter(
            client=user, status="completed"
        ).aggregate(total=Sum("amount"))
        total_spent = total_payments["total"] or Decimal("0.00")

        # Bu ay harcama
        this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        this_month_payments = ConsultationPayment.objects.filter(
            client=user, paid_at__gte=this_month_start
        ).aggregate(total=Sum("amount"))
        this_month_spent = this_month_payments["total"] or Decimal("0.00")

        # Aktif sözleşmeler
        active_contracts = ConsultantContract.objects.filter(
            client=user, status="active"
        ).count()

        # Favori mali müşavirler (en çok randevu alınan)
        favorite_consultants_qs = (
            ConsultationBooking.objects.filter(client=user, status="completed")
            .values("consultant__display_name")
            .annotate(booking_count=Count("id"))
            .order_by("-booking_count")[:5]
        )

        favorite_consultants = [
            {
                "name": item["consultant__display_name"],
                "booking_count": item["booking_count"],
            }
            for item in favorite_consultants_qs
        ]

        data = {
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "upcoming_bookings": upcoming_bookings,
            "total_spent": total_spent,
            "this_month_spent": this_month_spent,
            "active_contracts": active_contracts,
            "favorite_consultants": favorite_consultants,
        }

        serializer = ClientDashboardSerializer(data)
        return Response(serializer.data)
