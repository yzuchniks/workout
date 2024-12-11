import json
import httpx

API_URL = 'https://api.exchangerate-api.com/v4/latest/{currency}'


async def get_rate(scope, receive, send):
    path = scope['path']
    currency = path.strip('/')

    if not currency:
        currency = 'USD'

    api_url = API_URL.format(currency=currency)

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        data = response.json()

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'Content-Type', b'application/json']
        ]
    })

    await send({
        'type': 'http.response.body',
        'body': json.dumps(data).encode()
    })

application = get_rate
