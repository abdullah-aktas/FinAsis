# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError

def bad_request(request, exception=None):
    """400 Bad Request hatası için özel sayfa"""
    return render(request, 'errors/400.html', status=400)

def permission_denied(request, exception=None):
    """403 Permission Denied hatası için özel sayfa"""
    return render(request, 'errors/403.html', status=403)

def page_not_found(request, exception=None):
    """404 Page Not Found hatası için özel sayfa"""
    return render(request, 'errors/404.html', status=404)

def server_error(request):
    """500 Server Error hatası için özel sayfa"""
    return render(request, 'errors/500.html', status=500) 