# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.

# Oyun listesi view

def games(request):
    oyunlar = [
        {
            'title': 'TradeSim',
            'description': 'Şehirler arası ticaret yap, şirket yönet ve kar et!',
            'category': 'Ticaret',
            'image': 'img/games/trade.svg',
            'url': '/games/trade-sim/start/',
            'icon': 'bi-shop',
            'badge': 'Popüler',
            'color': 'primary'
        },
        {
            'title': 'Borsa Simülasyonu',
            'description': 'Sanal borsada alım-satım yaparak yatırım deneyimi kazanın.',
            'category': 'Yatırım',
            'image': 'img/games/stock.svg',
            'url': '/game-app/stock-market/',
            'icon': 'bi-graph-up-arrow',
            'badge': '',
            'color': 'info'
        },
        {
            'title': 'Bütçe Mücadelesi',
            'description': 'Gerçek hayat senaryolarıyla bütçe yönetimini öğrenin.',
            'category': 'Bütçe',
            'image': 'img/games/budget.svg',
            'url': '/game-app/budget-challenge/',
            'icon': 'bi-piggy-bank-fill',
            'badge': '',
            'color': 'warning'
        },
        {
            'title': 'Yatırım Simülatörü',
            'description': 'Yatırım stratejilerinizi test edin ve portföyünüzü büyütün.',
            'category': 'Portföy',
            'image': 'img/games/investment.svg',
            'url': '/game-app/investment-simulator/',
            'icon': 'bi-currency-dollar',
            'badge': '',
            'color': 'danger'
        },
        {
            'title': 'Finans Quiz',
            'description': 'Finansal bilginizi test edin, yeni kavramlar öğrenin.',
            'category': 'Eğitim',
            'image': 'img/games/quiz.svg',
            'url': '/game-app/quiz/',
            'icon': 'bi-patch-question-fill',
            'badge': '',
            'color': 'secondary'
        },
        {
            'title': 'FinQuest 3D',
            'description': '3D dünyada ticaret ve finansı deneyimleyin.',
            'category': 'Macera',
            'image': 'img/games/trade3d.svg',
            'url': '/finquest/game/',
            'icon': 'bi-box',
            'badge': '3D',
            'color': 'success'
        },
        {
            'title': 'Muhasebe Kayıt Oyunu',
            'description': 'Belgelere bakarak TDHP borç-alacak kayıtlarını oluşturun. Sürükle-bırak ile mobil uyumlu!',
            'category': 'Muhasebe',
            'image': 'img/games/ledger.svg',
            'url': '/game-app/ledger-game/',
            'icon': 'bi-file-earmark-text',
            'badge': 'Yeni',
            'color': 'purple'
        },
    ]
    return render(request, 'game_app/games.html', {'games': oyunlar})

# Her oyun için ayrı view

def stock_market_game(request):
    return render(request, 'game_app/stock_market.html')

def budget_challenge(request):
    return render(request, 'game_app/budget_challenge.html')

def investment_simulator(request):
    return render(request, 'game_app/investment_simulator.html')

def trade_trail_3d(request):
    return render(request, 'game_app/trade_trail_3d.html')

def tradesim(request):
    return render(request, 'game_app/tradesim.html')

def quiz(request):
    return render(request, 'game_app/quiz.html')

def ledger_game(request):
    """Muhasebe kayıt oyunu - belgeye dayalı TDHP eğitimi"""
    return render(request, 'game_app/ledger_game.html')

# Ek sayfalar (URL'lerde kullanılan)
def welcome(request):
    return render(request, 'game_app/welcome.html')

def scoreboard(request):
    """Basit skor tablosu placeholder.
    Gerçek skor verileri eklendiğinde bu view genişletilecektir.
    """
    scores = [
        {"user": "demo1", "score": 1200},
        {"user": "demo2", "score": 950},
        {"user": "demo3", "score": 870},
    ]
    return render(request, 'game_app/scoreboard.html', {"scores": scores})

def student_dashboard(request):
    return render(request, 'game_app/student_dashboard.html')

def investor_dashboard(request):
    return render(request, 'game_app/investor_dashboard.html')

def virtual_company_dashboard(request):
    return render(request, 'game_app/virtual_company_dashboard.html')

def kobi_dashboard(request):
    return render(request, 'game_app/kobi_dashboard.html')

def trade_trail(request):
    return render(request, 'game_app/trade_trail.html')

def game_detail(request, game_key):
    """Her oyun için detay sayfası"""
    # Oyun bilgileri (örnek, ileride veritabanı veya dict ile dinamik yapılabilir)
    games_info = {
        'tradesim': {
            'title': 'TradeSim & Ticaretin İzinde',
            'description': 'Şehirler arası ticaret, şirket yönetimi, finansal eğitim ve görevlerle birleşik simülasyon.',
            'image': '/static/img/games/tradesim.jpg',
            'how_to_play': 'Şirketini kur, şehirler arası ticaret yap, görevleri tamamla ve finansal okuryazarlığını geliştir.',
            'features': ['Şehirler arası ticaret', 'Şirket ve karakter yönetimi', 'Finansal eğitim', 'Görev ve başarımlar', 'Skor tablosu'],
            'play_url': '/games/game_app/tradesim/'
        },
        'stock-market': {
            'title': 'Borsa Simülasyonu',
            'description': 'Sanal borsada al-sat yaparak yatırım deneyimi kazan.',
            'image': '/static/img/games/stock.jpg',
            'how_to_play': 'Hisse senetlerini analiz et, al-sat yap, portföyünü büyüt.',
            'features': ['Gerçek zamanlı fiyatlar', 'Portföy yönetimi', 'Yatırım stratejileri'],
            'play_url': '/games/game_app/stock-market/'
        },
        'budget-challenge': {
            'title': 'Bütçe Mücadelesi',
            'description': 'Gerçek hayat senaryolarıyla bütçe yönetimini öğren.',
            'image': '/static/img/games/budget.jpg',
            'how_to_play': 'Gelir ve giderlerini yönet, tasarruf et, finansal hedeflere ulaş.',
            'features': ['Senaryo tabanlı', 'Gider analizi', 'Tasarruf ipuçları'],
            'play_url': '/games/game_app/budget-challenge/'
        },
        'investment-simulator': {
            'title': 'Yatırım Simülatörü',
            'description': 'Yatırım stratejilerini test et ve deneyim kazan.',
            'image': '/static/img/games/investment.jpg',
            'how_to_play': 'Farklı yatırım araçlarını dene, riskleri analiz et, portföyünü büyüt.',
            'features': ['Çeşitli yatırım araçları', 'Risk analizi', 'Getiri simülasyonu'],
            'play_url': '/games/game_app/investment-simulator/'
        },
        'trade-trail-3d': {
            'title': 'FinQuest 3D',
            'description': '3D dünyada ticaret ve finansı deneyimle.',
            'image': '/static/img/games/trade3d.jpg',
            'how_to_play': 'Karakterini seç, şirketini kur, 3D dünyada ticaret yap.',
            'features': ['3D ortam', 'Karakter ve şirket seçimi', 'Görevler ve eğitim'],
            'play_url': '/games/game_app/trade-trail-3d/'
        },
        'ledger-game': {
            'title': 'Muhasebe Kayıt Oyunu (TDHP)',
            'description': 'Belgelere dayalı muhasebe kayıtlarını öğrenin. Sürükle-bırak ile borç-alacak kayıtları oluşturun.',
            'image': '/static/img/games/ledger.jpg',
            'how_to_play': 'Belgeyi incele, hesap kartlarını sürükle, BORÇ ve ALACAK alanlarına bırak, kaydı kontrol et.',
            'features': ['Gerçek belge simülasyonu', 'TDHP hesap planı', 'Sürükle-bırak mekanizması', '5 farklı senaryo', 'Mobil uyumlu', 'Web tabanlı'],
            'play_url': '/game-app/ledger-game/'
        },
    }
    game = games_info.get(game_key)
    if not game:
        return render(request, 'game_app/game_not_found.html', {'game_key': game_key})
    return render(request, 'game_app/game_detail.html', {'game': game})
