from typing import List, Dict
import random
from datetime import datetime, time

class HealthAdvisor:
    def __init__(self):
        self.exercise_tips = [
            "💪 Masa başında omuz egzersizleri yapın",
            "🧘‍♂️ 5 dakikalık masa başı yoga",
            "👐 El ve bilek germe hareketleri",
            "👀 Göz egzersizleri yapın"
        ]
        
        self.wellness_challenges = [
            {
                "title": "Su Kahramanı",
                "target": "Günde 8 bardak su için",
                "reward": 100
            },
            {
                "title": "Mola Şampiyonu",
                "target": "Düzenli mola verin",
                "reward": 150
            }
        ]
    
    def get_personalized_advice(self, user_stats: Dict) -> Dict:
        """Kişiselleştirilmiş sağlık tavsiyeleri"""
        current_hour = datetime.now().hour
        
        advice = {
            "urgent": [],
            "daily": [],
            "wellness_challenge": random.choice(self.wellness_challenges)
        }
        
        # Gün içi önerileri
        if 9 <= current_hour <= 17:
            advice["urgent"].extend([
                "🪑 Postürünüzü kontrol edin",
                "💻 Ekran mesafenizi ayarlayın (40-70 cm)",
                "🌿 Derin bir nefes alın"
            ])
        
        # Yorgunluk analizi
        if user_stats["total_session_time"] > 120:
            advice["urgent"].append("⚠️ Uzun süredir çalışıyorsunuz. Biraz temiz hava almaya ne dersiniz?")
        
        return advice
