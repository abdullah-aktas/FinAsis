from django.urls import path, include

urlpatterns = [
    path('interactive-exercises/', include('apps.education.interactive_exercises.urls')),
] 