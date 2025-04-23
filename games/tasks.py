from celery import shared_task
from django.core.cache import cache
from .models import Game, Player, Transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_game_state():
    """Oyun durumunu güncelle"""
    active_games = Game.objects.filter(is_active=True)
    for game in active_games:
        try:
            # Oyun durumunu güncelle
            game.updated_at = timezone.now()
            game.save()
            
            # Önbelleği güncelle
            cache_key = f'game_state_{game.id}'
            cache.set(cache_key, {
                'id': game.id,
                'name': game.name,
                'updated_at': game.updated_at.isoformat()
            }, timeout=300)
            
            logger.info(f"Game {game.id} state updated successfully")
        except Exception as e:
            logger.error(f"Error updating game {game.id}: {str(e)}")

@shared_task
def process_transaction(transaction_id):
    """İşlemleri işle"""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        player = transaction.player
        
        # Bakiyeyi güncelle
        if transaction.transaction_type == 'income':
            player.current_balance += transaction.amount
        elif transaction.transaction_type == 'expense':
            player.current_balance -= transaction.amount
            
        player.save()
        
        # Önbelleği güncelle
        cache_key = f'player_balance_{player.id}'
        cache.set(cache_key, player.current_balance, timeout=300)
        
        logger.info(f"Transaction {transaction_id} processed successfully")
    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {str(e)}")

@shared_task
def cleanup_inactive_games():
    """Aktif olmayan oyunları temizle"""
    inactive_games = Game.objects.filter(
        is_active=False,
        updated_at__lt=timezone.now() - timezone.timedelta(days=30)
    )
    
    for game in inactive_games:
        try:
            # İlgili kayıtları temizle
            game.players.all().delete()
            game.transactions.all().delete()
            game.delete()
            
            logger.info(f"Game {game.id} cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up game {game.id}: {str(e)}") 