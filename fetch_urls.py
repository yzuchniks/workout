import asyncio
import json
from typing import Dict, List

import aiohttp
from aiohttp import ClientError


async def fetch_url(session: aiohttp.ClientSession, url: str) -> Dict:
    try:
        async with session.get(url, timeout=10) as response:
            return {
                'url': url,
                'status_cod': response.status
            }
    except (ClientError, asyncio.TimeoutError):
        return {
                'url': url,
                'status_cod': 0
            }


async def fetch_urls(urls: List[str], file_path: str):
    semaphore = asyncio.Semaphore(5)

    async def fetch_with_limit(url):
        async with semaphore:
            return await fetch_url(session, url)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_limit(url) for url in urls]
        for task in asyncio.as_completed(tasks):
            result = await task
            with open(file_path, 'a') as file:
                file.write(json.dumps(result) + '\n')

    print(f'Результаты записаны в файл {file_path}')


if __name__ == '__main__':
    urls = [
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url"
    ]
    asyncio.run(fetch_urls(urls, './results.jsonl'))
