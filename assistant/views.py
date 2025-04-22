from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import PagePrompt

class PagePromptListView(ListView):
    model = PagePrompt
    template_name = 'assistant/pageprompt_list.html'
    context_object_name = 'prompts'

class PagePromptDetailView(DetailView):
    model = PagePrompt
    template_name = 'assistant/pageprompt_detail.html'
    context_object_name = 'prompt'

class PagePromptCreateView(CreateView):
    model = PagePrompt
    template_name = 'assistant/pageprompt_form.html'
    fields = ['title', 'content', 'page_type', 'is_active']
    success_url = reverse_lazy('assistant:pageprompt_list')

class PagePromptUpdateView(UpdateView):
    model = PagePrompt
    template_name = 'assistant/pageprompt_form.html'
    fields = ['title', 'content', 'page_type', 'is_active']
    success_url = reverse_lazy('assistant:pageprompt_list')

class PagePromptDeleteView(DeleteView):
    model = PagePrompt
    template_name = 'assistant/pageprompt_confirm_delete.html'
    success_url = reverse_lazy('assistant:pageprompt_list') 