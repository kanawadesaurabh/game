from django.contrib import admin
from .models import CustomUser, GameRound, Bet, Transaction, KYCVerification, ChatMessage

admin.site.register(CustomUser)
admin.site.register(GameRound)
admin.site.register(Bet)
admin.site.register(KYCVerification)
admin.site.register(ChatMessage)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # इथे आपण डॅशबोर्डवर दिसण्यासाठी utr_number आणि upi_id ॲड केले आहेत
    list_display = ['user', 'amount', 'transaction_type', 'status', 'utr_number', 'upi_id', 'created_at']
    list_filter = ['status', 'transaction_type']