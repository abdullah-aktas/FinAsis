# -*- coding: utf-8 -*-
"""
Çek ve senet işlemleri ile ilgili görünümler
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Q

from permissions.decorators import permission_required

# Burada çek ve senet işlemleri ile ilgili view'ler olacak 