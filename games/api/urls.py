from django.urls import path
from .views import earn_badge, save_simulation_score

urlpatterns = [
    path('badge/earn/', earn_badge, name='earn_badge'),
    path('simulation/score/', save_simulation_score, name='save_simulation_score'),
] 