from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
    3D Ticaretin İzinde oyunu için view fonksiyonu.
    Kullanıcılar Türkiye'nin farklı şehirlerinde ticaret yaparak finansal stratejiler geliştirir.
    """
    if request.method == 'POST':
        # Oyun mantığı burada işlenecek
        pass
    
    context = {
        'title': 'Ticaretin İzinde 3D',
        'description': 'Türkiye\'nin farklı şehirlerinde ticaret yaparak finansal stratejiler geliştirin.',
        'initial_resources': {
            'gold': 1000,
            'goods': [],
            'reputation': 0
        },
        'cities': [
            {'name': 'Mardin', 'goods': ['Antik Eser', 'El Yapımı Halı', 'Baharat']},
            {'name': 'Ankara', 'goods': ['Tiftik', 'Mobilya', 'Teknoloji']},
            {'name': 'İzmir', 'goods': ['Zeytinyağı', 'İncir', 'Üzüm']},
            {'name': 'Denizli', 'goods': ['Pamuk', 'Tekstil', 'Mermer']},
            {'name': 'Erzurum', 'goods': ['Oltu Taşı', 'Bal', 'Peynir']},
            {'name': 'Muş', 'goods': ['Kırmızı Mercimek', 'Bal', 'Yün']}
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
