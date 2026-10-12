from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True) 
    location = models.CharField(max_length=255, blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    is_kyc_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class GameRound(models.Model): 
    round_number = models.AutoField(primary_key=True)
    start_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    winning_number = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Round {self.round_number}"

class Bet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE)
    chosen_number = models.IntegerField() 
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.bet_amount} on {self.chosen_number}"

class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (('ADD', 'Add Money'), ('WITHDRAW', 'Withdraw Money'))
    STATUS_CHOICES = (('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'))

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    utr_number = models.CharField(max_length=20, blank=True, null=True)
    upi_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ₹{self.amount} ({self.status})"

class KYCVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    aadhar_number = models.CharField(max_length=12, unique=True)
    pan_number = models.CharField(max_length=10, unique=True)
    is_verified = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KYC - {self.user.username} - Verified: {self.is_verified}"