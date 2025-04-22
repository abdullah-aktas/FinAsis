"""
Generic views for core application
"""
from django.views.generic import TemplateView, View, ListView, DetailView
from django.shortcuts import render, redirect
from django.http import JsonResponse
import psutil
import os
import datetime

def system_status():
    """
    Sistem durumunu döndürür
    """
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'process_count': len(psutil.pids()),
        'uptime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    } 