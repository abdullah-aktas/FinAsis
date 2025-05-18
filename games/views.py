# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Game, Player, Transaction, Challenge, PlayerChallenge
from .forms import GameForm, PlayerForm, TransactionForm, ChallengeForm
from ursina_game.game_manager import GameManager

@login_required
def game_list(request):
    games = Game.objects.filter(is_active=True)
    return render(request, 'games/game_list.html', {'games': games})

@login_required
def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    player = Player.objects.filter(user=request.user, game=game).first()
    challenges = Challenge.objects.filter(game=game)
    player_challenges = PlayerChallenge.objects.filter(player=player) if player else None
    
    context = {
        'game': game,
        'player': player,
        'challenges': challenges,
        'player_challenges': player_challenges
    }
    return render(request, 'games/game_detail.html', context)

@login_required
def join_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if not Player.objects.filter(user=request.user, game=game).exists():
        Player.objects.create(
            user=request.user,
            game=game,
            company_name=f"{request.user.username}'s Company",
            initial_balance=10000,
            current_balance=10000
        )
        messages.success(request, 'Oyuna başarıyla katıldınız!')
    return redirect('game_detail', pk=pk)

@login_required
def make_transaction(request, pk):
    player = get_object_or_404(Player, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.player = player
            transaction.save()
            
            # Update player's balance
            if transaction.transaction_type == 'income':
                player.current_balance += transaction.amount
            elif transaction.transaction_type == 'expense':
                player.current_balance -= transaction.amount
            player.save()
            
            messages.success(request, 'İşlem başarıyla gerçekleştirildi.')
            return redirect('game_detail', pk=player.game.pk)
    else:
        form = TransactionForm()
    
    return render(request, 'games/transaction_form.html', {'form': form, 'player': player})

@login_required
def complete_challenge(request, pk):
    player_challenge = get_object_or_404(PlayerChallenge, pk=pk, player__user=request.user)
    if not player_challenge.is_completed:
        player_challenge.is_completed = True
        player_challenge.completed_at = timezone.now()
        player_challenge.save()
        
        # Update player's score
        player = player_challenge.player
        player.score += player_challenge.challenge.points
        player.save()
        
        messages.success(request, 'Görev başarıyla tamamlandı!')
    return redirect('game_detail', pk=player_challenge.player.game.pk)

@login_required
def start_game(request, game_id):
    """Oyunu başlatır ve Ursina oyununa yönlendirir"""
    game = get_object_or_404(Game, id=game_id)
    player, created = Player.objects.get_or_create(
        user=request.user,
        game=game,
        defaults={
            'company_name': f"{request.user.username}'s Company",
            'initial_balance': 10000,
            'current_balance': 10000
        }
    )
    
    return render(request, 'games/game.html', {
        'game': game,
        'player': player
    })

@login_required
def get_game_state(request, player_id):
    """Oyun durumunu döndürür"""
    player = get_object_or_404(Player, id=player_id, user=request.user)
    game_manager = GameManager(player_id)
    
    return JsonResponse(game_manager.get_player_data())

@login_required
def save_game_state(request, player_id):
    """Oyun durumunu kaydeder"""
    if request.method == 'POST':
        player = get_object_or_404(Player, id=player_id, user=request.user)
        game_manager = GameManager(player_id)
        
        game_state = request.POST.get('game_state')
        if game_state:
            game_manager.save_game_state(game_state)
            return JsonResponse({'status': 'success'})
            
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def record_transaction(request, player_id):
    """Oyuncu işlemini kaydeder"""
    if request.method == 'POST':
        player = get_object_or_404(Player, id=player_id, user=request.user)
        game_manager = GameManager(player_id)
        
        transaction_type = request.POST.get('type')
        amount = float(request.POST.get('amount', 0))
        description = request.POST.get('description', '')
        
        if transaction_type and amount:
            game_manager.record_transaction(transaction_type, amount, description)
            return JsonResponse({'status': 'success'})
            
    return JsonResponse({'status': 'error'}, status=400) 