from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('place-bet/', views.place_bet, name='place_bet'),
    path('submit-transaction/', views.submit_transaction, name='submit_transaction'),
    path('auto-result/', views.auto_result, name='auto_result'),
    path('history/', views.history, name='history'), # <--- हे नवीन हिस्ट्री पेज
    path('get-messages/', views.get_messages, name='get_messages'),
    path('send-message/', views.send_message, name='send_message'),
]