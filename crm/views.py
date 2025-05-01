# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    LoyaltyProgram, LoyaltyLevel, CustomerLoyalty,
    SeasonalCampaign, PartnershipProgram, Partner,
    InteractionLog
)
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, F, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
import logging
from .models import (
    Customer, Contact, Opportunity, Activity,
    Document, Communication, Note
)
from .serializers import (
    CustomerSerializer, ContactSerializer,
    OpportunitySerializer, ActivitySerializer,
    DocumentSerializer, CommunicationSerializer,
    NoteSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsCustomerOwner,
    CanManageOpportunities, CanManageActivities,
    CanManageDocuments, CanManageCommunications,
    CanViewCustomerDetails, CanViewOpportunityDetails,
    CanViewActivityDetails, CanViewDocumentDetails,
    CanViewCommunicationDetails, IsInSalesTeam,
    IsInCustomerServiceTeam, IsInManagementTeam,
    CanExportData, CanImportData, CanDeleteRecords,
    CanViewReports, CanManageSettings
)
from .filters import (
    CustomerFilter, ContactFilter,
    OpportunityFilter, ActivityFilter,
    DocumentFilter, CommunicationFilter
)

logger = logging.getLogger(__name__)

# LoyaltyProgram Views
class LoyaltyProgramListView(LoginRequiredMixin, ListView):
    model = LoyaltyProgram
    template_name = 'crm/loyaltyprogram_list.html'
    context_object_name = 'programs'

class LoyaltyProgramDetailView(LoginRequiredMixin, DetailView):
    model = LoyaltyProgram
    template_name = 'crm/loyaltyprogram_detail.html'

class LoyaltyProgramCreateView(LoginRequiredMixin, CreateView):
    model = LoyaltyProgram
    template_name = 'crm/loyaltyprogram_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:loyaltyprogram_list')

class LoyaltyProgramUpdateView(LoginRequiredMixin, UpdateView):
    model = LoyaltyProgram
    template_name = 'crm/loyaltyprogram_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:loyaltyprogram_list')

class LoyaltyProgramDeleteView(LoginRequiredMixin, DeleteView):
    model = LoyaltyProgram
    template_name = 'crm/loyaltyprogram_confirm_delete.html'
    success_url = reverse_lazy('crm:loyaltyprogram_list')

# LoyaltyLevel Views
class LoyaltyLevelListView(LoginRequiredMixin, ListView):
    model = LoyaltyLevel
    template_name = 'crm/loyaltylevel_list.html'
    context_object_name = 'levels'

class LoyaltyLevelDetailView(LoginRequiredMixin, DetailView):
    model = LoyaltyLevel
    template_name = 'crm/loyaltylevel_detail.html'

class LoyaltyLevelCreateView(LoginRequiredMixin, CreateView):
    model = LoyaltyLevel
    template_name = 'crm/loyaltylevel_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:loyaltylevel_list')

class LoyaltyLevelUpdateView(LoginRequiredMixin, UpdateView):
    model = LoyaltyLevel
    template_name = 'crm/loyaltylevel_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:loyaltylevel_list')

class LoyaltyLevelDeleteView(LoginRequiredMixin, DeleteView):
    model = LoyaltyLevel
    template_name = 'crm/loyaltylevel_confirm_delete.html'
    success_url = reverse_lazy('crm:loyaltylevel_list')

# CustomerLoyalty Views
class CustomerLoyaltyListView(LoginRequiredMixin, ListView):
    model = CustomerLoyalty
    template_name = 'crm/customerloyalty_list.html'
    context_object_name = 'loyalties'

class CustomerLoyaltyDetailView(LoginRequiredMixin, DetailView):
    model = CustomerLoyalty
    template_name = 'crm/customerloyalty_detail.html'

class CustomerLoyaltyCreateView(LoginRequiredMixin, CreateView):
    model = CustomerLoyalty
    template_name = 'crm/customerloyalty_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:customerloyalty_list')

class CustomerLoyaltyUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomerLoyalty
    template_name = 'crm/customerloyalty_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:customerloyalty_list')

class CustomerLoyaltyDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomerLoyalty
    template_name = 'crm/customerloyalty_confirm_delete.html'
    success_url = reverse_lazy('crm:customerloyalty_list')

# SeasonalCampaign Views
class SeasonalCampaignListView(LoginRequiredMixin, ListView):
    model = SeasonalCampaign
    template_name = 'crm/seasonalcampaign_list.html'
    context_object_name = 'campaigns'

class SeasonalCampaignDetailView(LoginRequiredMixin, DetailView):
    model = SeasonalCampaign
    template_name = 'crm/seasonalcampaign_detail.html'

class SeasonalCampaignCreateView(LoginRequiredMixin, CreateView):
    model = SeasonalCampaign
    template_name = 'crm/seasonalcampaign_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:seasonalcampaign_list')

class SeasonalCampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = SeasonalCampaign
    template_name = 'crm/seasonalcampaign_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:seasonalcampaign_list')

class SeasonalCampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = SeasonalCampaign
    template_name = 'crm/seasonalcampaign_confirm_delete.html'
    success_url = reverse_lazy('crm:seasonalcampaign_list')

# PartnershipProgram Views
class PartnershipProgramListView(LoginRequiredMixin, ListView):
    model = PartnershipProgram
    template_name = 'crm/partnershipprogram_list.html'
    context_object_name = 'programs'

class PartnershipProgramDetailView(LoginRequiredMixin, DetailView):
    model = PartnershipProgram
    template_name = 'crm/partnershipprogram_detail.html'

class PartnershipProgramCreateView(LoginRequiredMixin, CreateView):
    model = PartnershipProgram
    template_name = 'crm/partnershipprogram_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:partnershipprogram_list')

class PartnershipProgramUpdateView(LoginRequiredMixin, UpdateView):
    model = PartnershipProgram
    template_name = 'crm/partnershipprogram_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:partnershipprogram_list')

class PartnershipProgramDeleteView(LoginRequiredMixin, DeleteView):
    model = PartnershipProgram
    template_name = 'crm/partnershipprogram_confirm_delete.html'
    success_url = reverse_lazy('crm:partnershipprogram_list')

# Partner Views
class PartnerListView(LoginRequiredMixin, ListView):
    model = Partner
    template_name = 'crm/partner_list.html'
    context_object_name = 'partners'

class PartnerDetailView(LoginRequiredMixin, DetailView):
    model = Partner
    template_name = 'crm/partner_detail.html'

class PartnerCreateView(LoginRequiredMixin, CreateView):
    model = Partner
    template_name = 'crm/partner_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:partner_list')

class PartnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Partner
    template_name = 'crm/partner_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:partner_list')

class PartnerDeleteView(LoginRequiredMixin, DeleteView):
    model = Partner
    template_name = 'crm/partner_confirm_delete.html'
    success_url = reverse_lazy('crm:partner_list')

# InteractionLog Views
class InteractionLogListView(LoginRequiredMixin, ListView):
    model = InteractionLog
    template_name = 'crm/interactionlog_list.html'
    context_object_name = 'logs'

class InteractionLogDetailView(LoginRequiredMixin, DetailView):
    model = InteractionLog
    template_name = 'crm/interactionlog_detail.html'

class InteractionLogCreateView(LoginRequiredMixin, CreateView):
    model = InteractionLog
    template_name = 'crm/interactionlog_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:interactionlog_list')

class InteractionLogUpdateView(LoginRequiredMixin, UpdateView):
    model = InteractionLog
    template_name = 'crm/interactionlog_form.html'
    fields = '__all__'
    success_url = reverse_lazy('crm:interactionlog_list')

class InteractionLogDeleteView(LoginRequiredMixin, DeleteView):
    model = InteractionLog
    template_name = 'crm/interactionlog_confirm_delete.html'
    success_url = reverse_lazy('crm:interactionlog_list')

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomerViewSet(viewsets.ModelViewSet):
    """Müşteri yönetimi için viewset"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomerFilter
    permission_classes = [
        IsAdminOrReadOnly | IsCustomerOwner,
        CanViewCustomerDetails
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """Müşterinin iletişim kişilerini listeler"""
        customer = self.get_object()
        contacts = customer.contacts.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def opportunities(self, request, pk=None):
        """Müşterinin fırsatlarını listeler"""
        customer = self.get_object()
        opportunities = customer.opportunities.all()
        serializer = OpportunitySerializer(opportunities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Müşterinin aktivitelerini listeler"""
        customer = self.get_object()
        activities = Activity.objects.filter(
            Q(opportunity__customer=customer) |
            Q(customer=customer)
        )
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Müşterinin dokümanlarını listeler"""
        customer = self.get_object()
        documents = customer.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def communications(self, request, pk=None):
        """Müşterinin iletişim kayıtlarını listeler"""
        customer = self.get_object()
        communications = customer.communications.all()
        serializer = CommunicationSerializer(communications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """Müşterinin notlarını listeler"""
        customer = self.get_object()
        notes = customer.notes.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Müşteri istatistiklerini getirir"""
        if not request.user.has_perm('crm.view_reports'):
            return Response(
                {'error': 'Bu işlem için yetkiniz yok.'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.get_queryset()
        stats = {
            'total_customers': queryset.count(),
            'active_customers': queryset.filter(is_active=True).count(),
            'by_industry': queryset.values('industry').annotate(count=Count('id')),
            'by_risk_level': queryset.values('risk_level').annotate(count=Count('id')),
            'total_revenue': queryset.aggregate(total=Sum('annual_revenue'))['total'],
            'avg_credit_score': queryset.aggregate(avg=Avg('credit_score'))['avg'],
        }
        return Response(stats)

class ContactViewSet(viewsets.ModelViewSet):
    """İletişim kişisi yönetimi için viewset"""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter
    permission_classes = [CanManageContacts]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(customer__owner=self.request.user) |
                Q(created_by=self.request.user)
            )
        return queryset

class OpportunityViewSet(viewsets.ModelViewSet):
    """Fırsat yönetimi için viewset"""
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OpportunityFilter
    permission_classes = [CanManageOpportunities, CanViewOpportunityDetails]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(customer__owner=self.request.user) |
                Q(assigned_to=self.request.user)
            )
        return queryset

    @action(detail=True, methods=['post'])
    def update_stage(self, request, pk=None):
        """Fırsat aşamasını günceller"""
        opportunity = self.get_object()
        new_stage = request.data.get('stage')
        
        if new_stage not in dict(Opportunity.STAGE_CHOICES):
            return Response(
                {'error': 'Geçersiz aşama.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        opportunity.stage = new_stage
        opportunity.save()
        return Response({'status': 'Aşama güncellendi.'})

class ActivityViewSet(viewsets.ModelViewSet):
    """Aktivite yönetimi için viewset"""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ActivityFilter
    permission_classes = [CanManageActivities, CanViewActivityDetails]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(opportunity__customer__owner=self.request.user) |
                Q(assigned_to=self.request.user)
            )
        return queryset

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Aktiviteyi tamamlandı olarak işaretler"""
        activity = self.get_object()
        activity.completed = True
        activity.completed_at = timezone.now()
        activity.save()
        return Response({'status': 'Aktivite tamamlandı.'})

class DocumentViewSet(viewsets.ModelViewSet):
    """Doküman yönetimi için viewset"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DocumentFilter
    permission_classes = [CanManageDocuments, CanViewDocumentDetails]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(customer__owner=self.request.user) |
                Q(uploaded_by=self.request.user)
            )
        return queryset

class CommunicationViewSet(viewsets.ModelViewSet):
    """İletişim kaydı yönetimi için viewset"""
    queryset = Communication.objects.all()
    serializer_class = CommunicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommunicationFilter
    permission_classes = [CanManageCommunications, CanViewCommunicationDetails]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(customer__owner=self.request.user) |
                Q(created_by=self.request.user)
            )
        return queryset

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """İletişim kaydını okundu olarak işaretler"""
        communication = self.get_object()
        communication.is_read = True
        communication.read_at = timezone.now()
        communication.save()
        return Response({'status': 'İletişim kaydı okundu olarak işaretlendi.'})

class NoteViewSet(viewsets.ModelViewSet):
    """Not yönetimi için viewset"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(customer__owner=self.request.user) |
                Q(created_by=self.request.user)
            )
        return queryset 