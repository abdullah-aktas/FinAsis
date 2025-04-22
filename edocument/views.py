from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import EDespatchAdviceLog

class EDespatchAdviceLogListView(ListView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_list.html'
    context_object_name = 'logs'

class EDespatchAdviceLogDetailView(DetailView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_detail.html'
    context_object_name = 'log'

class EDespatchAdviceLogCreateView(CreateView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_form.html'
    fields = ['despatch_advice', 'status', 'message', 'error_details']
    success_url = reverse_lazy('edocument:edespatchadvicelog_list')

class EDespatchAdviceLogUpdateView(UpdateView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_form.html'
    fields = ['despatch_advice', 'status', 'message', 'error_details']
    success_url = reverse_lazy('edocument:edespatchadvicelog_list')

class EDespatchAdviceLogDeleteView(DeleteView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_confirm_delete.html'
    success_url = reverse_lazy('edocument:edespatchadvicelog_list') 