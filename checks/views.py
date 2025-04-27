from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Check

# Create your views here.

@login_required
def check_list(request):
    checks = Check.objects.filter(user=request.user)
    return render(request, 'checks/check_list.html', {'checks': checks})

@login_required
def check_detail(request, pk):
    check = get_object_or_404(Check, pk=pk, user=request.user)
    return render(request, 'checks/check_detail.html', {'check': check})
