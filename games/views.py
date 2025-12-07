# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from .models import Game

# Burada artık model importu yok. Eğer yeni view fonksiyonu ekleyecekseniz buraya yazabilirsiniz.


def game_home(request):
    return render(request, "games/home.html")


def game_accounting(request):
    return render(request, "games/accounting.html")


def game_trading(request):
    return render(request, "games/trading.html")


def game_investing(request):
    return render(request, "games/investing.html")


def game_social(request):
    return render(request, "games/social.html")


def game_collection(request):
    return render(request, "games/collection.html")


def game_achievements(request):
    return render(request, "games/achievements.html")


def game_inventory(request):
    return render(request, "games/inventory.html")


def game_tax(request):
    return render(request, "games/tax.html")


def game_learning(request):
    return render(request, "games/learning.html")


def game_market(request):
    return render(request, "games/market.html")


def games_home(request):
    return render(request, "games/games_home.html")


def home(request):
    return render(request, "games/home.html")


def index(request):
    # Kullanıcıları doğrudan oynanabilir oyunlar listesine yönlendir
    return redirect("/games/game_app/games/")


def leaderboard_page(request):
    """Liderlik tablosu sayfası"""
    return render(request, "games/leaderboard.html")


def detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    return render(request, "games/detail.html", {"game": game})


def quest_bridge(request):
    """
    Görev Köprüsü - FinQuest görevlerini sınıf hedefleriyle eşleştirme aracı
    Öğretmenler için görev ve ders planı entegrasyon sayfası
    """
    from django.contrib.auth.views import redirect_to_login
    from games.task_engine import get_tasks
    from games.models import PlayerProfile

    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    # Kullanıcı profil bilgileri
    try:
        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    except Exception:
        profile = None

    # FinQuest görevleri
    try:
        finquest_tasks = get_tasks(audience="student", kind="mission", limit=20) or []
    except Exception:
        finquest_tasks = []

    # Eğitim görevleri (öğretmen ise)
    education_tasks = []
    try:
        from django.apps import apps

        if apps.is_installed("education"):
            from education.models import Task as EducationTask

            if (
                hasattr(request.user, "teacher_profile")
                or request.user.groups.filter(name__icontains="teacher").exists()
            ):
                try:
                    education_tasks = EducationTask.objects.filter(
                        created_by=request.user, is_active=True
                    )[:20]
                except Exception:
                    pass
    except Exception:
        pass

    # Eşleştirilmiş görevler
    matched_quests = []

    context = {
        "profile": profile,
        "finquest_tasks": finquest_tasks,
        "education_tasks": education_tasks,
        "matched_quests": matched_quests,
    }

    return render(request, "games/quest_bridge.html", context)
