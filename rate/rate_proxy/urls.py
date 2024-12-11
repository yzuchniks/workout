from django.urls import path
from .views import CurrencyRateView

urlpatterns = [
    path('<str:currency>/', CurrencyRateView.as_view(), name='currency_rate'),
]
