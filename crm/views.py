from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    LoyaltyProgram, LoyaltyLevel, CustomerLoyalty,
    SeasonalCampaign, PartnershipProgram, Partner,
    InteractionLog
)

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