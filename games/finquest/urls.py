# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = "finquest"

urlpatterns = [
    path("play/", views.play, name="game"),
    path("start/", views.start, name="start_game"),
    path("pause/", views.pause, name="pause_game"),
    path("resume/", views.resume, name="resume_game"),
    path("end/", views.end, name="end_game"),
    path("status/", views.status, name="status"),
    path("restart/", views.restart, name="restart_game"),
]
