# -*- coding: utf-8 -*-
import json
import os
from django.conf import settings
from games.models import Player, Transaction, Challenge, PlayerChallenge
from django.utils import timezone

class GameManager:
    def __init__(self, player_id):
        self.player = Player.objects.get(id=player_id)
        self.load_game_data()
        
    def load_game_data(self):
        """JSON dosyalarından oyun verilerini yükler"""
        base_path = os.path.join(settings.BASE_DIR, 'games', 'ursina_game')
        
        with open(os.path.join(base_path, 'blocks.json'), 'r', encoding='utf-8') as f:
            self.blocks = json.load(f)
            
        with open(os.path.join(base_path, 'workers.json'), 'r', encoding='utf-8') as f:
            self.workers = json.load(f)
            
        with open(os.path.join(base_path, 'economy.json'), 'r', encoding='utf-8') as f:
            self.economy = json.load(f)
            
    def save_game_state(self, game_state):
        """Oyun durumunu kaydeder"""
        # Oyun durumunu JSON olarak kaydet
        save_path = os.path.join(settings.MEDIA_ROOT, 'game_saves', f'player_{self.player.id}.json')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(game_state, f, ensure_ascii=False, indent=4)
            
    def record_transaction(self, transaction_type, amount, description):
        """Oyuncu işlemini kaydeder"""
        Transaction.objects.create(
            player=self.player,
            transaction_type=transaction_type,
            amount=amount,
            description=description
        )
        
        # Bakiye güncelleme
        if transaction_type == 'income':
            self.player.current_balance += amount
        else:
            self.player.current_balance -= amount
        self.player.save()
        
    def check_challenges(self, game_state):
        """Görevleri kontrol eder ve tamamlananları işaretler"""
        for challenge in Challenge.objects.filter(game=self.player.game):
            if not PlayerChallenge.objects.filter(player=self.player, challenge=challenge).exists():
                pc = PlayerChallenge.objects.create(player=self.player, challenge=challenge)
                
                # Görev kontrolü
                if self._is_challenge_completed(challenge, game_state):
                    pc.is_completed = True
                    pc.completed_at = timezone.now()
                    pc.save()
                    
                    # Puan güncelleme
                    self.player.score += challenge.points
                    self.player.save()
                    
    def _is_challenge_completed(self, challenge, game_state):
        """Görevin tamamlanıp tamamlanmadığını kontrol eder"""
        # Görev kontrolü mantığı burada implemente edilecek
        return False
        
    def get_player_data(self):
        """Oyuncu verilerini döndürür"""
        return {
            'id': self.player.id,
            'company_name': self.player.company_name,
            'balance': float(self.player.current_balance),
            'score': self.player.score,
            'active_challenges': list(PlayerChallenge.objects.filter(
                player=self.player,
                is_completed=False
            ).values('challenge__title', 'challenge__description', 'challenge__points'))
        } 