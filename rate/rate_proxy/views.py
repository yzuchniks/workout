import httpx
from django.http import JsonResponse
from django.views import View

API_URL = "https://api.exchangerate-api.com/v4/latest/{currency}"


class CurrencyRateView(View):
    async def get(self, request, currency):
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL.format(currency=currency))
            data = response.json()

        if 'rates' not in data:
            return JsonResponse(
                {'error': 'Несуществующие валюта или данные.'},
                status=404
            )

        return JsonResponse(data)
