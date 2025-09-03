from django.http import HttpResponse, JsonResponse
from .models import City, Character, Quest, CharacterQuest, Tournament, TournamentEntry, GameNotification, ChatMessage, Product, CityMarket, QrReward, UserQrReward
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework import generics, permissions
from .serializers import CharacterSerializer, QuestSerializer, CharacterQuestSerializer, TournamentSerializer, TournamentEntrySerializer, GameNotificationSerializer, ChatMessageSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .services import update_city_market, process_city_trade, random_market_event

def start_game(request):
    return HttpResponse('TradeSim oyunu başlatıldı! (Demo endpoint)')

def leaderboard(request):
    return HttpResponse('TradeSim Liderlik Tablosu (Demo endpoint)')

def stats(request):
    return HttpResponse('TradeSim İstatistikler (Demo endpoint)')

def city_list(request):
    cities = City.objects.all()
    data = [
        {
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'sectors': c.sectors,
            'market_size': c.market_size,
            'coordinates': c.coordinates,
            'neighbors': list(c.neighbors.values_list('id', flat=True)),
        } for c in cities
    ]
    return JsonResponse({'cities': data})

def city_detail(request, city_id):
    try:
        c = City.objects.get(id=city_id)
        data = {
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'sectors': c.sectors,
            'market_size': c.market_size,
            'coordinates': c.coordinates,
            'neighbors': list(c.neighbors.values_list('id', flat=True)),
            'sector_markets': c.sector_markets,
        }
        return JsonResponse({'city': data})
    except City.DoesNotExist:
        return JsonResponse({'error': 'Şehir bulunamadı'}, status=404)

@csrf_exempt
def trade_between_cities(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST bekleniyor'}, status=400)
    try:
        body = json.loads(request.body)
        from_id = body.get('from_city')
        to_id = body.get('to_city')
        sector = body.get('sector')
        amount = body.get('amount', 1)
        from_city = City.objects.get(id=from_id)
        to_city = City.objects.get(id=to_id)
        # Basit fiyat ve talep güncelleme mantığı
        from_price = from_city.sector_markets.get(sector, {}).get('price', 100)
        to_price = to_city.sector_markets.get(sector, {}).get('price', 100)
        profit = (to_price - from_price) * amount
        # Talep/arz güncellemesi örnek
        from_city.sector_markets.setdefault(sector, {'price': from_price, 'demand': 100})
        to_city.sector_markets.setdefault(sector, {'price': to_price, 'demand': 100})
        from_city.sector_markets[sector]['demand'] += amount
        to_city.sector_markets[sector]['demand'] -= amount
        from_city.save()
        to_city.save()
        return JsonResponse({'status': 'ok', 'profit': profit, 'from_city': from_city.name, 'to_city': to_city.name})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

class CharacterListCreateView(generics.ListCreateAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Character.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CharacterDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Character.objects.filter(user=self.request.user)

class QuestListView(generics.ListAPIView):
    serializer_class = QuestSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Quest.objects.filter(is_active=True)

class CharacterQuestListCreateView(generics.ListCreateAPIView):
    serializer_class = CharacterQuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        character_id = self.kwargs.get('character_id')
        return CharacterQuest.objects.filter(character__id=character_id, character__user=self.request.user)

    def perform_create(self, serializer):
        character_id = self.kwargs.get('character_id')
        character = Character.objects.get(id=character_id, user=self.request.user)
        serializer.save(character=character)

class CharacterQuestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CharacterQuestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return CharacterQuest.objects.filter(character__user=self.request.user)

class TournamentListCreateView(generics.ListCreateAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tournament.objects.all()

class TournamentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tournament.objects.all()
    lookup_field = 'pk'

class TournamentEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = TournamentEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tournament_id = self.kwargs.get('tournament_id')
        return TournamentEntry.objects.filter(tournament__id=tournament_id)

    def perform_create(self, serializer):
        tournament_id = self.kwargs.get('tournament_id')
        character_id = self.request.data.get('character_id')
        serializer.save(tournament_id=tournament_id, character_id=character_id)

class TournamentEntryDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TournamentEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    queryset = TournamentEntry.objects.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_story_suggestion(request, character_id):
    from .models import Character, CharacterQuest
    try:
        character = Character.objects.get(id=character_id, user=request.user)
    except Character.DoesNotExist:
        return Response({'error': 'Karakter bulunamadı.'}, status=404)
    # Karakterin mevcut durumu
    durum = {
        'seviye': character.level,
        'şehir': character.city.name if character.city else None,
        'yetenekler': character.skills,
        'aktif_görevler': [cq.quest.name for cq in character.character_quests.filter(is_completed=False)],
    }
    # Dummy AI öneri (ileride LLM ile değiştirilebilir)
    if character.level < 3:
        oneri = f"{character.city.name} şehrinde yeni bir ticaret görevi alabilirsin!"
    elif 'Büyük Ticaret' not in durum['aktif_görevler']:
        oneri = "Büyük Ticaret görevine başla ve 10.000 coin kazan!"
    else:
        oneri = "Yeni bir şehir keşfet ve orada yatırım yap!"
    return Response({'karakter': character.name, 'öneri': oneri, 'durum': durum})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_market_suggestion(request):
    from .models import City
    city_id = request.data.get('city_id')
    sector = request.data.get('sector')
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        return Response({'error': 'Şehir bulunamadı.'}, status=404)
    sector_data = city.sector_markets.get(sector, {'price': 100, 'demand': 100})
    # Dummy AI öneri (ileride LLM ile değiştirilebilir)
    fiyat = sector_data['price']
    talep = sector_data['demand']
    if talep > 120:
        oneri = f"{sector} sektöründe talep çok yüksek! Fiyatlar artabilir, yatırım fırsatı var."
    elif fiyat < 80:
        oneri = f"{sector} sektöründe fiyatlar düşük, stok yapabilirsin."
    else:
        oneri = f"{sector} sektöründe pazar dengede, dikkatli ol."
    return Response({'şehir': city.name, 'sektör': sector, 'fiyat': fiyat, 'talep': talep, 'öneri': oneri})

class NotificationListView(generics.ListAPIView):
    serializer_class = GameNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return GameNotification.objects.filter(user=self.request.user).order_by('-created_at')

class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = GameNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = GameNotification.objects.all()
    lookup_field = 'pk'
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'error': 'Yetkisiz.'}, status=status.HTTP_403_FORBIDDEN)
        instance.is_read = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        room = self.request.query_params.get('room')
        qs = ChatMessage.objects.filter(is_deleted=False)
        if room:
            qs = qs.filter(room=room)
        return qs.order_by('created_at')
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatMessageReportView(generics.UpdateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChatMessage.objects.all()
    lookup_field = 'pk'
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_reported = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@api_view(['GET'])
def product_list(request):
    """Tüm ürünleri listeler."""
    products = Product.objects.all()
    data = [
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'base_price': p.base_price,
            'unit': p.unit,
            'category': p.category
        } for p in products
    ]
    return Response({'products': data})

@api_view(['GET'])
def city_market_list(request, city_id):
    """Bir şehrin tüm pazarlarını (ürün, fiyat, arz, talep) listeler."""
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        return Response({'error': 'Şehir bulunamadı.'}, status=404)
    markets = CityMarket.objects.filter(city=city)
    data = [
        {
            'product': m.product.name,
            'product_id': m.product.id,
            'price': m.price,
            'supply': m.supply,
            'demand': m.demand,
            'last_updated': m.last_updated
        } for m in markets
    ]
    return Response({'city': city.name, 'markets': data})

@api_view(['POST'])
def city_trade(request):
    """Şehirler arası ticaret işlemi başlatır."""
    from_id = request.data.get('from_city')
    to_id = request.data.get('to_city')
    product_id = request.data.get('product_id')
    amount = int(request.data.get('amount', 1))
    try:
        from_city = City.objects.get(id=from_id)
        to_city = City.objects.get(id=to_id)
        product = Product.objects.get(id=product_id)
    except (City.DoesNotExist, Product.DoesNotExist):
        return Response({'error': 'Şehir veya ürün bulunamadı.'}, status=404)
    try:
        result = process_city_trade(from_city, to_city, product, amount)
        return Response({'status': 'ok', 'result': result})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def trigger_market_event(request):
    """Bir şehirdeki ürün için rastgele pazar olayı tetikler."""
    city_id = request.data.get('city_id')
    product_id = request.data.get('product_id')
    try:
        city = City.objects.get(id=city_id)
        product = Product.objects.get(id=product_id)
        market = CityMarket.objects.get(city=city, product=product)
    except (City.DoesNotExist, Product.DoesNotExist, CityMarket.DoesNotExist):
        return Response({'error': 'Şehir, ürün veya pazar bulunamadı.'}, status=404)
    event = random_market_event(market)
    return Response({'status': 'ok', 'event': event, 'market': {
        'product': market.product.name,
        'price': market.price,
        'supply': market.supply,
        'demand': market.demand
    }})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def qr_reward(request):
    code = request.data.get('code')
    user = request.user
    try:
        qr = QrReward.objects.get(code=code, is_active=True)
    except QrReward.DoesNotExist:
        return Response({'status': 'error', 'message': 'Geçersiz veya pasif QR kod.'}, status=400)
    if UserQrReward.objects.filter(user=user, qr_reward=qr).exists():
        return Response({'status': 'error', 'message': 'Bu QR kodu zaten kullandınız.'}, status=400)
    # Ödül ver
    UserQrReward.objects.create(user=user, qr_reward=qr)

    # --- ÖDÜLÜ KULLANICIYA UYGULA ---
    reward = qr.reward
    # 1. Coin ekle
    if 'coins' in reward:
        character = user.characters.first()
        if character:
            character.score += int(reward['coins'])
            character.save()
    # 2. Rozet ekle (choices içinde 'badges' listesi)
    if 'badge' in reward:
        character = user.characters.first()
        if character:
            badges = character.choices.get('badges', []) if character.choices else []
            if reward['badge'] not in badges:
                badges.append(reward['badge'])
                character.choices['badges'] = badges
                character.save()
    # 3. Görev ekle (quest_id ile)
    if 'quest_id' in reward:
        from .models import Quest, CharacterQuest
        character = user.characters.first()
        if character:
            quest = Quest.objects.filter(id=reward['quest_id']).first()
            if quest and not CharacterQuest.objects.filter(character=character, quest=quest).exists():
                CharacterQuest.objects.create(character=character, quest=quest)
    # ---------------------------------

    return Response({'status': 'ok', 'message': f'Tebrikler! {qr.description} - Ödül: {qr.reward}'}) 