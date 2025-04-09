from django.urls import path
from . import views

app_name = 'virtual_company'

urlpatterns = [
    path('', views.company_home, name='home'),
    path('create/', views.create_company, name='create_company'),
    path('my-company/', views.my_company, name='my_company'),
    path('market/', views.market, name='market'),
    path('competitors/', views.competitors, name='competitors'),
] 