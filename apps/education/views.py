from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def kobi_tutorials(request):
    return render(request, 'education/kobi_tutorials.html') 