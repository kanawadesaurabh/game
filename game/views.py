from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import GameRound, Bet, Transaction, KYCVerification, ChatMessage
import json
import random
from decimal import Decimal

@login_required(login_url='login')
def index(request):
    current_round = GameRound.objects.filter(is_active=True).first()
    active_bets = Bet.objects.filter(user=request.user, game_round=current_round) if current_round else []
    last_round = GameRound.objects.filter(is_active=False).order_by('-round_number').first()
    last_win = last_round.winning_number if last_round else "-"
    
    return render(request, 'game/index.html', {'active_bets': active_bets, 'last_win': last_win})

@login_required(login_url='login')
def place_bet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chosen_number = int(data.get('number'))
            bet_amount = Decimal(str(data.get('amount')))
            user = request.user 
            
            current_round = GameRound.objects.filter(is_active=True).first()
            if not current_round:
                current_round = GameRound.objects.create(is_active=True)

            user_bets = Bet.objects.filter(user=user, game_round=current_round)
            bet_numbers = set([bet.chosen_number for bet in user_bets]) 
            
            if chosen_number not in bet_numbers and len(bet_numbers) >= 3:
                return JsonResponse({'status': 'error', 'message': '❌ तुम्ही एका राउंडमध्ये जास्तीत जास्त ३ नंबरवरच बेट लावू शकता!'})

            if user.wallet_balance >= bet_amount:
                user.wallet_balance -= bet_amount
                user.save()
                Bet.objects.create(user=user, game_round=current_round, chosen_number=chosen_number, bet_amount=bet_amount)
                return JsonResponse({'status': 'success', 'message': f'बेट यशस्वी! नंबर {chosen_number} वर ₹{bet_amount} लावले.', 'new_balance': str(user.wallet_balance)})
            else:
                return JsonResponse({'status': 'error', 'message': 'तुमच्या वॉलेटमध्ये पुरेसे पैसे नाहीत!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}) 
    return JsonResponse({'status': 'error'})

@login_required(login_url='login')
def submit_transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = float(data.get('amount'))
        trans_type = data.get('type')
        utr = data.get('utr', '')
        upi = data.get('upi', '')

        Transaction.objects.create(user=request.user, amount=amount, transaction_type=trans_type, status='PENDING', utr_number=utr, upi_id=upi)
        return JsonResponse({'status': 'success', 'message': 'तुमची रिक्वेस्ट ॲडमिनला पाठवली आहे.'})
    return JsonResponse({'status': 'error'})

@login_required(login_url='login')
def auto_result(request):
    if request.method == 'POST':
        current_round = GameRound.objects.filter(is_active=True).first()
        if not current_round:
            return JsonResponse({'status': 'error', 'message': 'कोणताही गेम चालू नाही!'})
        
        all_bets = Bet.objects.filter(game_round=current_round)
        total_pool = sum([bet.bet_amount for bet in all_bets])
        
        payouts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for bet in all_bets:
            payouts[bet.chosen_number] += bet.bet_amount * 6
            
        max_payout_allowed = total_pool * Decimal('0.70')
        safe_numbers = [num for num, payout in payouts.items() if payout <= max_payout_allowed]
        
        winning_number = random.choice(safe_numbers) if safe_numbers else random.randint(1, 6)
        
        current_round.winning_number = winning_number
        current_round.is_active = False
        current_round.save()
        
        for bet in all_bets.filter(chosen_number=winning_number):
            winner = bet.user
            winnings = bet.bet_amount * 6
            winner.wallet_balance += winnings
            winner.save()
            
        GameRound.objects.create(is_active=True)
        return JsonResponse({'status': 'success', 'winning_number': winning_number})

@login_required(login_url='login')
def history(request):
    user_bets = Bet.objects.filter(user=request.user).order_by('-created_at')[:30]
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:30]
    return render(request, 'game/history.html', {'bets': user_bets, 'transactions': user_transactions})

def get_messages(request):
    messages = ChatMessage.objects.all().order_by('-created_at')[:50]
    msgs_data = [{'user': msg.user.username, 'message': msg.message} for msg in reversed(messages)]
    return JsonResponse({'messages': msgs_data})

def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ChatMessage.objects.create(user=request.user, message=data.get('message'))
        return JsonResponse({'status': 'success'})