from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from django.templatetags.static import static

# Create your views here.

@api_view(['GET'])
def game_list(request):
    # Örnek oyun listesi
    games = [
        {
            'id': 1,
            'title': 'Finansal Kelime Oyunu',
            'description': 'Finansal terimleri öğrenin ve puan kazanın',
            'image': 'https://via.placeholder.com/150',
            'highScore': 850,
        },
        {
            'id': 2,
            'title': 'Bütçe Simülasyonu',
            'description': 'Gerçek hayat senaryolarıyla bütçe yönetimini öğrenin',
            'image': 'https://via.placeholder.com/150',
            'highScore': 1200,
        },
        {
            'id': 3,
            'title': 'Yatırım Yarışması',
            'description': 'Yatırım stratejilerinizi test edin',
            'image': 'https://via.placeholder.com/150',
            'highScore': 0,
        },
    ]
    return Response(games)

@api_view(['GET'])
def game_detail(request, pk):
    # Örnek oyun detayı
    game = {
        'id': pk,
        'title': 'Finansal Kelime Oyunu',
        'description': 'Finansal terimleri öğrenin ve puan kazanın',
        'image': 'https://via.placeholder.com/150',
        'highScore': 850,
        'instructions': 'Oyun talimatları burada yer alacak',
        'difficulty': 'Orta',
        'estimatedTime': '15 dakika',
    }
    return Response(game)

def games_home(request):
    return render(request, 'game_app/home.html')

def stock_market_game(request):
    return render(request, 'game_app/stock_market.html')

def budget_challenge(request):
    return render(request, 'game_app/budget_challenge.html')

def investment_simulator(request):
    return render(request, 'game_app/investment_simulator.html')

def trade_trail(request):
    """
    Ticaretin İzinde oyunu için view fonksiyonu.
    Kullanıcılar İpek Yolu'nda ticaret yaparak finansal stratejiler geliştirir.
    """
    if request.method == 'POST':
        # Oyun mantığı burada işlenecek
        pass
    
    context = {
        'title': 'Ticaretin İzinde',
        'description': 'Tarihi İpek Yolu\'nda ticaret yaparak finansal stratejiler geliştirin.',
        'initial_resources': {
            'gold': 1000,
            'goods': [],
            'reputation': 0
        },
        'cities': [
            {'name': 'İstanbul', 'goods': ['İpek', 'Baharat', 'Porselen']},
            {'name': 'Bağdat', 'goods': ['Halı', 'Baharat', 'Mücevher']},
            {'name': 'Şam', 'goods': ['Cam', 'Tekstil', 'Baharat']},
            {'name': 'Buhara', 'goods': ['İpek', 'Halı', 'Mücevher']},
            {'name': 'Kaşgar', 'goods': ['Baharat', 'Porselen', 'Tekstil']}
        ]
    }
    
    return render(request, 'game_app/trade_trail.html', context)

def trade_trail_3d(request):
    """
    Ursina engine ile geliştirilmiş 3D ticaret simülasyonu oyununu başlatır.
    """
    from ursina_game.game import run_game
    import threading
    import sys
    
    # Oyunu ayrı bir thread'de başlat
    def start_game_thread():
        try:
            run_game()
        except Exception as e:
            print(f"Oyun çalıştırılırken hata oluştu: {e}", file=sys.stderr)
    
    # Oyunu başlat
    game_thread = threading.Thread(target=start_game_thread)
    game_thread.daemon = True  # Ana thread sonlandığında bu thread de sonlanacak
    game_thread.start()
    
    context = {
        'title': '3D Ticaret Simülasyonu',
        'description': 'Gerçekçi bir 3D ortamda ticaret ve borsa deneyimi yaşayın.',
        'controls': [
            {'key': 'W, A, S, D', 'action': 'Hareket etme'},
            {'key': 'Mouse', 'action': 'Kamera kontrolü'},
            {'key': 'Left Click', 'action': 'Şirket seçimi ve butonlara tıklama'},
            {'key': 'ESC', 'action': 'Oyundan çıkış'}
        ],
        'tips': [
            'Piyasa değişimlerini takip ederek alım-satım yapın.',
            'Şirketlerin volatilitelerini göz önünde bulundurun.',
            'Farklı sektörlere yatırım yaparak riskinizi dağıtın.',
            'Günlük ekonomik haberleri takip edin.'
        ]
    }
    
    return render(request, 'game_app/trade_trail_3d.html', context)

def welcome(request):
    """
    Karşılama sayfası ve kullanıcı tipi seçimi.
    """
    return render(request, 'game_app/welcome.html')

def student_dashboard(request):
    """
    Öğrenci kullanıcıları için özel dashboard.
    """
    context = {
        'title': 'Öğrenci Paneli',
        'games': [
            {
                'name': 'Ticaretin İzinde 3D',
                'description': 'Türkiye\'nin farklı şehirlerinde ticaret yaparak finansal stratejiler geliştirin.',
                'url': 'trade_trail_3d',
                'difficulty': 'Başlangıç',
                'icon': 'fa-map-marked-alt'
            },
            {
                'name': 'Borsa Simülatörü',
                'description': 'Gerçek piyasa verileri ile borsa deneyimi kazanın.',
                'url': 'stock_simulator',
                'difficulty': 'Orta',
                'icon': 'fa-chart-line'
            },
            {
                'name': 'Finansal Matematik',
                'description': 'Finansal hesaplamaları oyunlaştırılmış şekilde öğrenin.',
                'url': 'financial_math',
                'difficulty': 'Başlangıç',
                'icon': 'fa-calculator'
            }
        ]
    }
    return render(request, 'game_app/student_dashboard.html', context)

def investor_dashboard(request):
    """
    Yatırımcı kullanıcıları için özel dashboard.
    """
    context = {
        'title': 'Yatırımcı Paneli',
        'tools': [
            {
                'name': 'Portföy Yönetimi',
                'description': 'Sanal portföyünüzü oluşturun ve yönetin.',
                'url': 'portfolio_manager',
                'icon': 'fa-briefcase'
            },
            {
                'name': 'Teknik Analiz',
                'description': 'Gelişmiş teknik analiz araçları ile piyasayı analiz edin.',
                'url': 'technical_analysis',
                'icon': 'fa-chart-bar'
            },
            {
                'name': 'Risk Analizi',
                'description': 'Yatırım risklerinizi hesaplayın ve yönetin.',
                'url': 'risk_analysis',
                'icon': 'fa-shield-alt'
            }
        ]
    }
    return render(request, 'game_app/investor_dashboard.html', context)

def virtual_company_dashboard(request):
    """
    Sanal şirket kullanıcıları için özel dashboard.
    """
    context = {
        'title': 'Sanal Şirket Paneli',
        'features': [
            {
                'name': 'Şirket Yönetimi',
                'description': 'Sanal şirketinizi yönetin ve büyütün.',
                'url': 'company_management',
                'icon': 'fa-building'
            },
            {
                'name': 'Finansal Planlama',
                'description': 'Şirket finansmanı ve bütçe planlaması yapın.',
                'url': 'financial_planning',
                'icon': 'fa-file-invoice-dollar'
            },
            {
                'name': 'Pazar Analizi',
                'description': 'Pazar araştırması ve rekabet analizi yapın.',
                'url': 'market_analysis',
                'icon': 'fa-search-dollar'
            }
        ]
    }
    return render(request, 'game_app/virtual_company_dashboard.html', context)

def kobi_dashboard(request):
    features = [
        {
            'name': 'Finansal Analiz',
            'description': 'Şirketinizin finansal durumunu analiz edin ve raporlar oluşturun.',
            'icon': 'fas fa-chart-line',
            'url': 'financial_analysis'
        },
        {
            'name': 'Bütçe Planlama',
            'description': 'Bütçenizi planlayın ve finansal hedeflerinizi belirleyin.',
            'icon': 'fas fa-wallet',
            'url': 'budget_planning'
        },
        {
            'name': 'Nakit Akışı',
            'description': 'Nakit akışınızı takip edin ve tahminler oluşturun.',
            'icon': 'fas fa-money-bill-wave',
            'url': 'cash_flow'
        },
        {
            'name': 'Yatırım Analizi',
            'description': 'Yatırım fırsatlarını değerlendirin ve kararlar alın.',
            'icon': 'fas fa-chart-pie',
            'url': 'investment_analysis'
        },
        {
            'name': 'Risk Yönetimi',
            'description': 'Finansal risklerinizi tanımlayın ve yönetin.',
            'icon': 'fas fa-shield-alt',
            'url': 'risk_management'
        },
        {
            'name': 'Raporlama',
            'description': 'Özelleştirilmiş finansal raporlar oluşturun.',
            'icon': 'fas fa-file-alt',
            'url': 'reporting'
        }
    ]
    
    context = {
        'title': 'KOBİ Dashboard',
        'features': features
    }
    
    return render(request, 'game_app/kobi_dashboard.html', context)

def games(request):
    """
    Oyunlar sayfasını gösterir.
    """
    context = {
        'games': [
            {
                'title': 'Bütçe Planlama Mücadelesi',
                'description': 'Kısıtlı bir bütçeyle işletmenizi büyütmeye çalışın ve finansal kararlar alın.',
                'url': reverse('game_app:budget_challenge'),
                'image': static('img/games/budget_challenge.jpg'),
                'category': 'finans'
            },
            {
                'title': 'Yatırım Simülatörü',
                'description': 'Farklı yatırım araçlarını keşfedin ve portföy yönetimini öğrenin.',
                'url': reverse('game_app:investment_simulator'),
                'image': static('img/games/investment_simulator.jpg'),
                'category': 'yatırım'
            },
            {
                'title': 'Borsa Oyunu',
                'description': 'Gerçek verilerle desteklenen sanal borsa ortamında alım-satım yapın.',
                'url': reverse('game_app:stock_market'),
                'image': static('img/games/stock_market.jpg'),
                'category': 'borsa'
            },
            {
                'title': 'Ticaret Yolu 3D',
                'description': '3D dünyada ticaret stratejileri geliştirin ve küresel pazarı öğrenin.',
                'url': reverse('game_app:trade_trail_3d'),
                'image': static('img/games/trade_trail_3d.jpg'),
                'category': 'ticaret'
            }
        ]
    }
    return render(request, 'game_app/games.html', context)
