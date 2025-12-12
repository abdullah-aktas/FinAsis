from django.http import JsonResponse, HttpRequest
from .models import (
    City,
    Character,
    Quest,
    CharacterQuest,
    Tournament,
    TournamentEntry,
    GameNotification,
    ChatMessage,
    Product,
    CityMarket,
    QrReward,
    UserQrReward,
)
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework import generics, permissions
from .serializers import (
    CharacterSerializer,
    QuestSerializer,
    CharacterQuestSerializer,
    TournamentSerializer,
    TournamentEntrySerializer,
    GameNotificationSerializer,
    ChatMessageSerializer,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .services import process_city_trade, random_market_event, market_tick
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import get_user_model
import uuid
from typing import cast
from rest_framework.request import Request
from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import QuerySet

# TradeSim E-Spor Zorluk Sistemi
from .difficulty_system import (
    DifficultyLevel,
    DIFFICULTY_CONFIGS,
    get_available_difficulties,
    get_recommended_difficulty,
    DIFFICULTY_UNLOCK_REQUIREMENTS,
)


def start_game(request):
    """TradeSim oyunu ana sayfası - Zorluk seçimi ile"""
    from games.models import PlayerProfile

    # Oyuncu profilini al
    profile = None
    available_difficulties = [DifficultyLevel.BEGINNER, DifficultyLevel.EASY]
    recommended = DifficultyLevel.NORMAL

    if request.user.is_authenticated:
        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

        # Erişilebilir zorluk seviyeleri
        available_difficulties = get_available_difficulties(
            profile.level, profile.elo_rating
        )

        # Win rate hesapla
        win_rate = (
            profile.games_won / profile.games_played
            if profile.games_played > 0
            else 0.5
        )
        recommended = get_recommended_difficulty(
            profile.level, profile.elo_rating, win_rate
        )

    # Zorluk bilgilerini template'e gönder
    difficulties_data = []
    for diff_level in DifficultyLevel:
        config = DIFFICULTY_CONFIGS[diff_level]
        is_available = diff_level in available_difficulties
        is_recommended = diff_level == recommended
        requirements = DIFFICULTY_UNLOCK_REQUIREMENTS[diff_level]

        difficulties_data.append(
            {
                "level": diff_level.value,
                "code": diff_level.name.lower(),
                "name": config.name,
                "description": config.description,
                "is_available": is_available,
                "is_recommended": is_recommended,
                "requirements": requirements,
                "ai_count": config.ai_count,
                "time_limit": config.time_limit_minutes,
                "xp_multiplier": config.xp_multiplier,
                "coin_multiplier": config.coin_multiplier,
            }
        )

    context = {
        "profile": profile,
        "difficulties": difficulties_data,
        "recommended_difficulty": recommended.value if recommended else 3,
    }

    return render(request, "trade_sim/start_game.html", context)


@login_required
def play_test(request):
    """Simple test page for debugging"""
    return render(request, "trade_sim/play_simple_test.html")


def debug_console(request):
    """Debug console for testing TradeSim APIs (DEVELOPMENT ONLY)"""
    from django.conf import settings

    # Production'da debug console'u kapat
    if getattr(settings, "DEBUG", False) is False:
        from django.http import Http404

        raise Http404("Debug console is only available in development mode")

    # Superuser kontrolü
    if not request.user.is_superuser:
        from django.contrib import messages
        from django.shortcuts import redirect

        messages.error(request, "Debug console sadece yöneticiler için erişilebilir.")
        return redirect("/games/trade-sim/start/")

    session = request.session.get("tradesim_game_session")
    context = {
        "game_session": session,
        "is_debug": True,
    }
    return render(request, "trade_sim/debug_console.html", context)


def play(request):
    """TradeSim gameplay screen.
    Expects a game session to be initialized via the start API.
    If not initialized, redirect users to the start page. Accepts optional
    ?difficulty=<int> to reflect selected difficulty on UI.
    """
    try:
        # Ensure logged in (start API requires auth; keep UX consistent)
        if not request.user.is_authenticated:
            return redirect("/accounts/login/?next=/games/trade-sim/start/")

        session = request.session.get("tradesim_game_session")

        # If there is a difficulty param but session missing, just keep it in context
        diff_param = request.GET.get("difficulty")
        difficulty_level = None
        difficulty_config = None
        if diff_param:
            try:
                from .difficulty_system import DifficultyLevel, DIFFICULTY_CONFIGS

                difficulty_level = DifficultyLevel(int(diff_param))
                difficulty_config = DIFFICULTY_CONFIGS.get(difficulty_level)
            except Exception:
                difficulty_level = None
                difficulty_config = None

        # If session not present, route user to difficulty/start page
        if session is None:
            # Friendly message via querystring so we don't need messages framework
            return redirect("/games/trade-sim/start/?need_session=1")

        # Session dict'ini normalize et - eksik key'leri default değerlerle doldur
        # Template'de güvenli erişim için tüm key'lerin mevcut olması gerekiyor
        if not isinstance(session, dict):
            session = {}
        
        # Template'de kullanılan tüm key'leri garanti altına al
        normalized_session = {
            "difficulty": session.get("difficulty", 1),
            "difficulty_name": session.get("difficulty_name", "Başlangıç"),
            "starting_capital": session.get("starting_capital", 10000),
            "current_capital": session.get("current_capital", session.get("starting_capital", 10000)),
            "current_city": session.get("current_city", "istanbul"),
            "total_trades": session.get("total_trades", 0),
            "profit_loss": session.get("profit_loss", 0),
            "victory_requirement": session.get("victory_requirement", 20000),
            "time_limit_minutes": session.get("time_limit_minutes", 30),
            "ai_count": session.get("ai_count", 0),
            "turn": session.get("turn", 0),
            "character_id": session.get("character_id"),
            "active_events": session.get("active_events", []),
            "multipliers": session.get("multipliers", {}),
        }
        # Orijinal session'daki diğer key'leri de koru
        normalized_session.update({k: v for k, v in session.items() if k not in normalized_session})

        # Character bilgisini al
        import json

        character = Character.objects.filter(user=request.user).first()
        character_data = None
        character_inventory_json = "{}"
        if character:
            try:
                # Eski kayıtlarda choices alanı None olabileceği için korumalı erişim kullan
                choices = character.choices or {}
                inventory = choices.get("inventory", {}) if isinstance(choices, dict) else {}
                character_inventory_json = json.dumps(inventory)
                character_data = {
                    "money": character.score or 0,
                    "inventory": inventory,
                    "city": character.city.name if character.city else "İstanbul",
                    "level": character.level or 1,
                }
            except Exception as e:
                # Character verisi alınırken hata olursa, boş değerlerle devam et
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Character data error in play view: {e}", exc_info=True)
                character_data = {
                    "money": 10000,
                    "inventory": {},
                    "city": "İstanbul",
                    "level": 1,
                }
                character_inventory_json = "{}"

        context = {
            "game_session": normalized_session,
            "difficulty_param": (
                int(diff_param) if diff_param and diff_param.isdigit() else None
            ),
            "difficulty_config": difficulty_config,
            "character": character_data,
            "character_inventory_json": character_inventory_json,
        }
        return render(request, "trade_sim/play.html", context)
    except Exception as e:
        # Tüm hataları yakala ve logla, sonra kullanıcıyı start sayfasına yönlendir
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in trade-sim play view: {e}", exc_info=True)
        # Hata durumunda kullanıcıyı start sayfasına yönlendir
        return redirect("/games/trade-sim/start/?error=1")


def leaderboard(request):
    """TradeSim Liderlik Tablosu - E-spor kullanıcılarına göre sıralama"""
    from django.db.models import Q
    from games.models import PlayerProfile, GameSession, Game
    from datetime import timedelta
    from django.utils import timezone

    # TradeSim oyununu bul
    try:
        tradesim_game = Game.objects.get(name="TradeSim")
    except Game.DoesNotExist:
        tradesim_game = None

    # Farklı sıralama türleri
    sort_by = request.GET.get("sort", "total_score")
    time_filter = request.GET.get("filter", "all_time")

    # Tüm oyuncuları al
    players = PlayerProfile.objects.select_related("user").all()

    # Zaman filtresi uygula
    if time_filter == "weekly":
        week_ago = timezone.now() - timedelta(days=7)
        # Son 1 haftadaki skorlar
        players = players.filter(updated_at__gte=week_ago)
    elif time_filter == "monthly":
        month_ago = timezone.now() - timedelta(days=30)
        players = players.filter(updated_at__gte=month_ago)

    # Sıralama
    if sort_by == "elo_rating":
        players = players.order_by("-elo_rating", "-total_score")
    elif sort_by == "mmr":
        players = players.order_by("-mmr", "-total_score")
    elif sort_by == "level":
        players = players.order_by("-level", "-xp", "-total_score")
    elif sort_by == "games_won":
        # games_won field zaten modelde var, annotation yerine direkt sırala
        players = players.order_by("-games_won", "-total_score")
    else:  # total_score (default)
        players = players.order_by("-total_score", "-elo_rating")

    # Kullanıcının kendi sıralaması (slice yapmadan önce hesapla)
    user_rank = None
    if request.user.is_authenticated:
        try:
            user_profile = PlayerProfile.objects.get(user=request.user)
            # Tüm listedeki sırasını bul
            all_players = PlayerProfile.objects.select_related("user").all()
            if time_filter == "weekly":
                week_ago = timezone.now() - timedelta(days=7)
                all_players = all_players.filter(updated_at__gte=week_ago)
            elif time_filter == "monthly":
                month_ago = timezone.now() - timedelta(days=30)
                all_players = all_players.filter(updated_at__gte=month_ago)

            # Aynı sıralama kriterini uygula
            if sort_by == "elo_rating":
                user_rank = (
                    all_players.filter(
                        Q(elo_rating__gt=user_profile.elo_rating)
                        | Q(
                            elo_rating=user_profile.elo_rating,
                            total_score__gt=user_profile.total_score,
                        )
                    ).count()
                    + 1
                )
            elif sort_by == "level":
                user_rank = (
                    all_players.filter(
                        Q(level__gt=user_profile.level)
                        | Q(level=user_profile.level, xp__gt=user_profile.xp)
                        | Q(
                            level=user_profile.level,
                            xp=user_profile.xp,
                            total_score__gt=user_profile.total_score,
                        )
                    ).count()
                    + 1
                )
            else:  # total_score veya diğerleri
                user_rank = (
                    all_players.filter(
                        Q(total_score__gt=user_profile.total_score)
                        | Q(
                            total_score=user_profile.total_score,
                            elo_rating__gt=user_profile.elo_rating,
                        )
                    ).count()
                    + 1
                )
        except PlayerProfile.DoesNotExist:
            pass

    # Top 100 ile sınırla
    players_list = list(players[:100])

    # Rank ataması
    leaderboard_data = []
    for index, player in enumerate(players_list, start=1):
        games_won = player.games_played - player.games_lost
        win_rate = (
            (games_won / player.games_played * 100) if player.games_played > 0 else 0
        )

        leaderboard_data.append(
            {
                "rank": index,
                "player": player,
                "games_won": games_won,
                "win_rate": round(win_rate, 1),
            }
        )

    # İstatistikler
    total_players = PlayerProfile.objects.count()
    total_games_played = GameSession.objects.count()

    context = {
        "leaderboard": leaderboard_data,
        "sort_by": sort_by,
        "time_filter": time_filter,
        "user_rank": user_rank,
        "total_players": total_players,
        "total_games_played": total_games_played,
        "game": tradesim_game,
    }

    return render(request, "trade_sim/leaderboard.html", context)


def stats(request):
    """TradeSim İstatistikler - Oyuncu istatistikleri ve analizler"""
    from games.models import PlayerProfile, GameSession
    from django.db.models import Avg
    from datetime import timedelta
    from django.utils import timezone

    # Kullanıcının profili
    user_profile = None
    user_sessions = []
    if request.user.is_authenticated:
        try:
            user_profile = PlayerProfile.objects.get(user=request.user)
            user_sessions = GameSession.objects.filter(player=request.user).order_by(
                "-started_at"
            )[:10]
        except PlayerProfile.DoesNotExist:
            pass

    # Genel istatistikler
    total_players = PlayerProfile.objects.count()
    total_sessions = GameSession.objects.count()

    # Ortalamalar
    avg_stats = PlayerProfile.objects.aggregate(
        avg_level=Avg("level"),
        avg_elo=Avg("elo_rating"),
        avg_score=Avg("total_score"),
        avg_games=Avg("games_played"),
    )

    # En iyi oyuncular
    top_level = PlayerProfile.objects.order_by("-level").first()
    top_elo = PlayerProfile.objects.order_by("-elo_rating").first()
    top_score = PlayerProfile.objects.order_by("-total_score").first()

    # Son 7 günlük aktivite
    timezone.now() - timedelta(days=7)
    daily_activity = []
    for i in range(7):
        day = timezone.now() - timedelta(days=6 - i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        count = GameSession.objects.filter(
            started_at__gte=day_start, started_at__lt=day_end
        ).count()

        daily_activity.append(
            {
                "date": day.strftime("%d/%m"),
                "count": count,
            }
        )

    # Oyuncu dağılımı (rank bazlı)
    rank_distribution = []
    for rank_key, rank_name in PlayerProfile.RANK_CHOICES:
        count = PlayerProfile.objects.filter(rank=rank_key).count()
        rank_distribution.append(
            {
                "rank": rank_name,
                "count": count,
            }
        )

    context = {
        "user_profile": user_profile,
        "user_sessions": user_sessions,
        "total_players": total_players,
        "total_sessions": total_sessions,
        "avg_stats": avg_stats,
        "top_level": top_level,
        "top_elo": top_elo,
        "top_score": top_score,
        "daily_activity": daily_activity,
        "rank_distribution": rank_distribution,
    }

    return render(request, "trade_sim/stats.html", context)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def guest_onboarding(request: Request):
    """Kimliği doğrulanmamış ziyaretçiyi hızlıca oyuna al: geçici kullanıcı + karakter + pazar kurulumu ve oturum açma.
    Not: Geçici kullanıcılar 'guest-<id>' kullanıcı adı ile oluşturulur ve mevcut oturuma login edilir.
    """
    # Mevcut veri var mı kontrol et; yoksa minimum seed yap
    if not City.objects.exists():
        City.objects.create(
            name="Başlangıç",
            description="Yeni oyuncular için başlangıç şehri",
            sectors=["genel"],
            market_size=1000,
            coordinates={"x": 0, "y": 0},
        )
    if not Product.objects.exists():
        Product.objects.create(
            name="Buğday",
            description="Temel ürün",
            base_price=100,
            unit="adet",
            category="genel",
        )
    for city in City.objects.all():
        for product in Product.objects.all():
            CityMarket.objects.get_or_create(
                city=city,
                product=product,
                defaults={"price": product.base_price, "supply": 100, "demand": 100},
            )

    # Geçici kullanıcı oluştur ve oturuma al
    User = get_user_model()
    guest_suffix = uuid.uuid4().hex[:8]
    username = f"guest-{guest_suffix}"
    user = User.objects.create(username=username, email=f"{username}@example.invalid")
    user.set_unusable_password()
    user.save()

    # Karakter oluştur (sinyal de oluşturabilir; biz garantiye alıyoruz)
    default_city = City.objects.order_by("id").first()
    character = Character.objects.filter(user=user).first()
    if character is None:
        character = Character.objects.create(
            user=user, name=f"{username} Trader", city=default_city
        )

    # Başlangıç görevi ekle
    starter_quest, _ = Quest.objects.get_or_create(
        name="İlk Ticaret",
        defaults={
            "description": "İlk şehir ticaretini tamamla.",
            "quest_type": "side",
            "requirements": {"trade_count": 1},
            "rewards": {"coins": 100, "xp": 10},
            "is_active": True,
        },
    )
    CharacterQuest.objects.get_or_create(character=character, quest=starter_quest)

    # Oturumu login et
    try:
        base_req = request._request if hasattr(request, "_request") else request
        login(
            cast(HttpRequest, base_req),
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )
    except TypeError:
        # Eski versiyonlarda backend parametresi zorunlu olmayabilir
        base_req = request._request if hasattr(request, "_request") else request
        login(cast(HttpRequest, base_req), user)

    data = {
        "status": "ok",
        "user": {"id": user.pk, "username": user.username},
        "character": CharacterSerializer(character).data,
    }
    return Response(data, status=201)


@api_view(["POST", "GET"])
@permission_classes([permissions.IsAuthenticated])
def onboarding(request: Request):
    """Ensure the authenticated user has a playable setup: character, starter city/product markets, and a starter quest."""
    user = request.user
    character = Character.objects.filter(user=user).first()
    # Create character if missing (safety in case signal didn't run)
    if character is None:
        default_city = City.objects.order_by("id").first()
        character = Character.objects.create(
            user=user, name=f"{user.username} Trader", city=default_city
        )
    # Seed a simple starter quest if none
    starter_quest, _ = Quest.objects.get_or_create(
        name="İlk Ticaret",
        defaults={
            "description": "İlk şehir ticaretini tamamla.",
            "quest_type": "side",
            "requirements": {"trade_count": 1},
            "rewards": {"coins": 100, "xp": 10},
            "is_active": True,
        },
    )
    CharacterQuest.objects.get_or_create(character=character, quest=starter_quest)
    # Ensure at least one city, product and market entries exist so the game is playable
    if not City.objects.exists():
        City.objects.create(
            name="Başlangıç",
            description="Yeni oyuncular için başlangıç şehri",
            sectors=["genel"],
            market_size=1000,
            coordinates={"x": 0, "y": 0},
        )
    if not Product.objects.exists():
        Product.objects.create(
            name="Buğday",
            description="Temel ürün",
            base_price=100,
            unit="adet",
            category="genel",
        )
    # Create market rows for all city-product pairs if missing
    for city in City.objects.all():
        for product in Product.objects.all():
            CityMarket.objects.get_or_create(
                city=city,
                product=product,
                defaults={"price": product.base_price, "supply": 100, "demand": 100},
            )
    # Response
    char_data = CharacterSerializer(character).data
    quests = CharacterQuest.objects.filter(character=character)
    quest_data = CharacterQuestSerializer(quests, many=True).data
    return Response({"status": "ok", "character": char_data, "quests": quest_data})


def city_list(request: Request):
    cities = City.objects.all()
    data = [
        {
            "id": c.pk,
            "name": c.name,
            "description": c.description,
            "sectors": c.sectors,
            "market_size": c.market_size,
            "coordinates": c.coordinates,
            "neighbors": list(c.neighbors.values_list("id", flat=True)),
        }
        for c in cities
    ]
    return JsonResponse({"cities": data})


def city_detail(request: Request, city_id):
    try:
        c = City.objects.get(id=city_id)
        data = {
            "id": c.pk,
            "name": c.name,
            "description": c.description,
            "sectors": c.sectors,
            "market_size": c.market_size,
            "coordinates": c.coordinates,
            "neighbors": list(c.neighbors.values_list("id", flat=True)),
            "sector_markets": c.sector_markets,
        }
        return JsonResponse({"city": data})
    except City.DoesNotExist:
        return JsonResponse({"error": "Şehir bulunamadı"}, status=404)


@csrf_exempt
def trade_between_cities(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST bekleniyor"}, status=400)
    try:
        body = json.loads(request.body)
        from_id = body.get("from_city")
        to_id = body.get("to_city")
        sector = body.get("sector")
        amount = body.get("amount", 1)
        from_city = City.objects.get(id=from_id)
        to_city = City.objects.get(id=to_id)
        # Basit fiyat ve talep güncelleme mantığı
        from_price = from_city.sector_markets.get(sector, {}).get("price", 100)
        to_price = to_city.sector_markets.get(sector, {}).get("price", 100)
        profit = (to_price - from_price) * amount
        # Talep/arz güncellemesi örnek
        from_city.sector_markets.setdefault(
            sector, {"price": from_price, "demand": 100}
        )
        to_city.sector_markets.setdefault(sector, {"price": to_price, "demand": 100})
        from_city.sector_markets[sector]["demand"] += amount
        to_city.sector_markets[sector]["demand"] -= amount
        from_city.save()
        to_city.save()
        return JsonResponse(
            {
                "status": "ok",
                "profit": profit,
                "from_city": from_city.name,
                "to_city": to_city.name,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


class CharacterListCreateView(generics.ListCreateAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Character]:  # type: ignore
        return Character.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CharacterDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self) -> QuerySet[Character]:  # type: ignore
        return Character.objects.filter(user=self.request.user)


class QuestListView(generics.ListAPIView):
    serializer_class = QuestSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Quest.objects.filter(is_active=True)


class CharacterQuestListCreateView(generics.ListCreateAPIView):
    serializer_class = CharacterQuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[CharacterQuest]:  # type: ignore
        character_id = self.kwargs.get("character_id")
        return CharacterQuest.objects.filter(
            character__id=character_id, character__user=self.request.user
        )

    def perform_create(self, serializer):
        character_id = self.kwargs.get("character_id")
        character = Character.objects.get(id=character_id, user=self.request.user)
        serializer.save(character=character)


class CharacterQuestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CharacterQuestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self) -> QuerySet[CharacterQuest]:  # type: ignore
        return CharacterQuest.objects.filter(character__user=self.request.user)


class TournamentListCreateView(generics.ListCreateAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tournament.objects.all()


class TournamentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tournament.objects.all()
    lookup_field = "pk"


class TournamentEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = TournamentEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[TournamentEntry]:  # type: ignore
        tournament_id = self.kwargs.get("tournament_id")
        return TournamentEntry.objects.filter(tournament__id=tournament_id)

    def perform_create(self, serializer):
        tournament_id = self.kwargs.get("tournament_id")
        req_data = getattr(self.request, "data", self.request.POST)
        character_id = req_data.get("character_id")
        serializer.save(tournament_id=tournament_id, character_id=character_id)


class TournamentEntryDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TournamentEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
    queryset = TournamentEntry.objects.all()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def ai_story_suggestion(request, character_id):
    from .models import Character, CharacterQuest

    try:
        character = Character.objects.get(id=character_id, user=request.user)
    except Character.DoesNotExist:
        return Response({"error": "Karakter bulunamadı."}, status=404)
    # Karakterin mevcut durumu
    durum = {
        "seviye": character.level,
        "şehir": character.city.name if character.city else None,
        "yetenekler": character.skills,
        "aktif_görevler": [
            cq.quest.name
            for cq in CharacterQuest.objects.filter(
                character=character, is_completed=False
            )
        ],
    }
    # Dummy AI öneri (ileride LLM ile değiştirilebilir)
    city_name = character.city.name if character.city else "yakınındaki"
    if character.level < 3:
        oneri = f"{city_name} bir şehirde yeni bir ticaret görevi alabilirsin!"
    elif "Büyük Ticaret" not in durum["aktif_görevler"]:
        oneri = "Büyük Ticaret görevine başla ve 10.000 coin kazan!"
    else:
        oneri = "Yeni bir şehir keşfet ve orada yatırım yap!"
    return Response({"karakter": character.name, "öneri": oneri, "durum": durum})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def ai_market_suggestion(request: Request):
    from .models import City

    req_data = getattr(request, "data", None) or getattr(request, "POST", {})
    city_id = req_data.get("city_id")
    sector = req_data.get("sector")
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        return Response({"error": "Şehir bulunamadı."}, status=404)
    sector_data = city.sector_markets.get(sector, {"price": 100, "demand": 100})
    # Dummy AI öneri (ileride LLM ile değiştirilebilir)
    fiyat = sector_data["price"]
    talep = sector_data["demand"]
    if talep > 120:
        oneri = f"{sector} sektöründe talep çok yüksek! Fiyatlar artabilir, yatırım fırsatı var."
    elif fiyat < 80:
        oneri = f"{sector} sektöründe fiyatlar düşük, stok yapabilirsin."
    else:
        oneri = f"{sector} sektöründe pazar dengede, dikkatli ol."
    return Response(
        {
            "şehir": city.name,
            "sektör": sector,
            "fiyat": fiyat,
            "talep": talep,
            "öneri": oneri,
        }
    )


class NotificationListView(generics.ListAPIView):
    serializer_class = GameNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[GameNotification]:  # type: ignore
        return GameNotification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = GameNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = GameNotification.objects.all()
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"error": "Yetkisiz."}, status=status.HTTP_403_FORBIDDEN)
        instance.is_read = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[ChatMessage]:  # type: ignore
        room = getattr(self.request, "query_params", self.request.GET).get("room")
        qs = ChatMessage.objects.filter(is_deleted=False)
        if room:
            qs = qs.filter(room=room)
        return qs.order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatMessageReportView(generics.UpdateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChatMessage.objects.all()
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_reported = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def product_list(request: Request):
    """Tüm ürünleri listeler."""
    products = Product.objects.all()
    data = [
        {
            "id": p.pk,
            "name": p.name,
            "description": p.description,
            "base_price": p.base_price,
            "unit": p.unit,
            "category": p.category,
        }
        for p in products
    ]
    return Response({"products": data})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def city_market_list(request: Request, city_id):
    """Bir şehrin tüm pazarlarını (ürün, fiyat, arz, talep) listeler."""
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        return Response({"error": "Şehir bulunamadı."}, status=404)
    markets = CityMarket.objects.filter(city=city)
    data = [
        {
            "product": m.product.name,
            "product_id": getattr(m, "product_id"),
            "price": m.price,
            "supply": m.supply,
            "demand": m.demand,
            "last_updated": m.last_updated,
        }
        for m in markets
    ]
    return Response({"city": city.name, "markets": data})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def city_trade(request: Request):
    """Şehirler arası ticaret işlemi başlatır."""
    req_data = getattr(request, "data", None) or getattr(request, "POST", {})
    from_id = req_data.get("from_city")
    to_id = req_data.get("to_city")
    product_id = req_data.get("product_id")
    amount = int(req_data.get("amount", 1))
    try:
        from_city = City.objects.get(id=from_id)
        to_city = City.objects.get(id=to_id)
        product = Product.objects.get(id=product_id)
    except (City.DoesNotExist, Product.DoesNotExist):
        return Response({"error": "Şehir veya ürün bulunamadı."}, status=404)
    try:
        result = process_city_trade(from_city, to_city, product, amount)
        return Response({"status": "ok", "result": result})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def market_trade(request: Request):
    """Şehir pazarında al-sat işlemi yapar. Character ve inventory günceller."""
    req_data = getattr(request, "data", None) or getattr(request, "POST", {})

    action = req_data.get("action")  # 'buy' or 'sell'
    item_name = req_data.get("item_name") or req_data.get("product_name")
    amount = float(req_data.get("amount", 0))
    price = float(req_data.get("price", 0))
    req_data.get("city", "istanbul")

    if not all([action, item_name, amount > 0, price > 0]):
        return Response(
            {"success": False, "error": "Eksik veya geçersiz parametreler"}, status=400
        )

    if action not in ["buy", "sell"]:
        return Response({"success": False, "error": "Geçersiz işlem tipi"}, status=400)

    try:
        # Karakteri al
        character = Character.objects.filter(user=request.user).first()
        if not character:
            return Response(
                {"success": False, "error": "Karakter bulunamadı"}, status=404
            )

        # Inventory'yi al (JSON field) - eski kayıtlarda choices None olabilir
        choices = character.choices or {}
        inventory = choices.get("inventory", {})

        if action == "buy":
            # Satın alma işlemi
            total_cost = amount * price

            # Para kontrolü
            if character.score < total_cost:
                return Response(
                    {"success": False, "error": "Yeterli paranız yok!"}, status=400
                )

            # Para azalt, envantere ekle
            character.score -= int(total_cost)
            inventory[item_name] = inventory.get(item_name, 0) + amount

            result = {
                "action": "buy",
                "product": item_name,
                "amount": amount,
                "price": price,
                "total_cost": total_cost,
                "success": True,
                "message": f"{amount} {item_name} başarıyla satın alındı",
            }
        else:
            # Satış işlemi
            has_amount = inventory.get(item_name, 0)

            if has_amount < amount:
                return Response(
                    {"success": False, "error": "Envanterde yeterli ürün yok!"},
                    status=400,
                )

            total_gain = amount * price

            # Para ekle, envanterden çıkar
            character.score += int(total_gain)
            inventory[item_name] = has_amount - amount

            if inventory[item_name] <= 0:
                inventory.pop(item_name, None)

            result = {
                "action": "sell",
                "product": item_name,
                "amount": amount,
                "price": price,
                "total_gain": total_gain,
                "success": True,
                "message": f"{amount} {item_name} başarıyla satıldı",
            }

        # Güncelleri kaydet
        choices["inventory"] = inventory
        character.choices = choices
        character.save()

        return Response({"status": "ok", "result": result})

    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def change_city(request: Request):
    """Karakterin şehrini değiştirir ve seyahat maliyetini uygular."""
    req_data = getattr(request, "data", None) or getattr(request, "POST", {})

    city_id = req_data.get("city_id")
    travel_cost = float(req_data.get("cost", 0))

    try:
        # Karakter ve yeni şehri al
        character = Character.objects.filter(user=request.user).first()
        if not character:
            return Response(
                {"success": False, "error": "Karakter bulunamadı"}, status=404
            )

        new_city = City.objects.get(id=city_id)

        # Para kontrolü
        if character.score < travel_cost:
            return Response(
                {"success": False, "error": "Seyahat için yeterli paranız yok!"},
                status=400,
            )

        # Aynı şehir mi kontrolü
        if character.city and character.city.pk == new_city.pk:
            return Response(
                {"success": False, "error": "Zaten bu şehirdesiniz!"}, status=400
            )

        # Para azalt, şehri değiştir
        character.score -= int(travel_cost)
        character.city = new_city
        character.save()

        return Response(
            {
                "status": "ok",
                "city": {
                    "id": new_city.pk,
                    "name": new_city.name,
                },
                "remaining_money": character.score,
                "message": f"{new_city.name} şehrine başarıyla ulaştınız!",
            }
        )

    except City.DoesNotExist:
        return Response({"success": False, "error": "Şehir bulunamadı"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def trigger_market_event(request: Request):
    """Bir şehirdeki ürün için rastgele pazar olayı tetikler."""
    req_data = getattr(request, "data", None) or getattr(request, "POST", {})
    city_id = req_data.get("city_id")
    product_id = req_data.get("product_id")
    try:
        city = City.objects.get(id=city_id)
        product = Product.objects.get(id=product_id)
        market = CityMarket.objects.get(city=city, product=product)
    except (City.DoesNotExist, Product.DoesNotExist, CityMarket.DoesNotExist):
        return Response({"error": "Şehir, ürün veya pazar bulunamadı."}, status=404)
    event = random_market_event(market)
    return Response(
        {
            "status": "ok",
            "event": event,
            "market": {
                "product": market.product.name,
                "price": market.price,
                "supply": market.supply,
                "demand": market.demand,
            },
        }
    )


@api_view(["POST"])
def market_tick_view(request: Request):
    """Arz/talep değerlerini dengeye yaklaştıran bir piyasa adımı uygular."""
    req_data = getattr(request, "data", None) or getattr(request, "POST", {})
    city_id = req_data.get("city_id")
    city = None
    if city_id:
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return Response({"error": "Şehir bulunamadı."}, status=404)
    count = market_tick(city)
    return Response({"status": "ok", "updated": count})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def qr_reward(request: Request):
    req_data = getattr(request, "data", None) or getattr(request, "POST", {})
    code = req_data.get("code")
    user = request.user
    try:
        qr = QrReward.objects.get(code=code, is_active=True)
    except QrReward.DoesNotExist:
        return Response(
            {"status": "error", "message": "Geçersiz veya pasif QR kod."}, status=400
        )
    if UserQrReward.objects.filter(user=user, qr_reward=qr).exists():
        return Response(
            {"status": "error", "message": "Bu QR kodu zaten kullandınız."}, status=400
        )
    # Ödül ver
    UserQrReward.objects.create(user=user, qr_reward=qr)

    # --- ÖDÜLÜ KULLANICIYA UYGULA ---
    reward = qr.reward
    # 1. Coin ekle
    if "coins" in reward:
        character = Character.objects.filter(user=user).first()
        if character:
            character.score += int(reward["coins"])
            character.save()
    # 2. Rozet ekle (choices içinde 'badges' listesi)
    if "badge" in reward:
        character = Character.objects.filter(user=user).first()
        if character:
            badges = character.choices.get("badges", []) if character.choices else []
            if reward["badge"] not in badges:
                badges.append(reward["badge"])
                character.choices["badges"] = badges
                character.save()
    # 3. Görev ekle (quest_id ile)
    if "quest_id" in reward:
        from .models import Quest, CharacterQuest

        character = Character.objects.filter(user=user).first()
        if character:
            quest = Quest.objects.filter(id=reward["quest_id"]).first()
            if (
                quest
                and not CharacterQuest.objects.filter(
                    character=character, quest=quest
                ).exists()
            ):
                CharacterQuest.objects.create(character=character, quest=quest)
    # ---------------------------------

    return Response(
        {"status": "ok", "message": f"Tebrikler! {qr.description} - Ödül: {qr.reward}"}
    )
