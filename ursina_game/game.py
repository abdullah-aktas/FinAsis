from __future__ import absolute_import, unicode_literals
import os

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finasis.settings')

def run_game():
    from ursina import Entity, Vec3, color, window, Ursina
    from ursina.prefabs.first_person_controller import FirstPersonController
    from company_management.models import Company, Department, Employee

    # Ursina uygulamasını başlat
    app = Ursina()

    # Oyun ayarları
    analytics_data = {
        'market_analysis': {
            'stable_market_days': 0,
            'bull_market_days': 0,
            'bear_market_days': 0
        },
        'knowledge_progress': {},
        'daily_trades': [],
        'portfolio_history': [],
        'tournament_standings': {}
    }

    # Oyuncu verileri
    player = {
        'id': 1,
        'name': 'John Doe',
        'money': 100000,
        'portfolio': {
            'AAPL': {'shares': 10, 'price': 150},
            'GOOGL': {'shares': 5, 'price': 2000},
            'TSLA': {'shares': 8, 'price': 700}
        },
        'risk_tolerance': 0.7,
        'total_income': 10000,
        'total_savings': 50000,
        'total_debt': 20000,
        'debt_to_income': 0.2,
        'portfolio_diversity': 0.6,
        'risk_score': 0.7
    }

    # Oyun döngüsü
    def update():
        pass

    # Oyunu başlat
    window.title = 'FinAsis - Finansal Eğitim Simülasyonu'
    window.borderless = False
    window.fullscreen = False
    window.exit_button.visible = False
    window.fps_counter.enabled = True

    # Ana oyun döngüsünü başlat
    app.run()

if __name__ == '__main__':
    run_game() 