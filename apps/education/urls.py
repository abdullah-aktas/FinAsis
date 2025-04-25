from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('kobi-tutorials/', views.kobi_tutorials, name='kobi_tutorials'),
] 