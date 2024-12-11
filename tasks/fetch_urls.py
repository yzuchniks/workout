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


def package_generator(collection, size):
    package = []
    for item in collection:
        package.append(item)
        if len(package) >= size:
            yield package
            package = []
    if package:
        yield package


async def worker(
    queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    file_path: str
):
    with open(file_path, 'a') as file:
        while True:
            url = await queue.get()
            if url is None:
                break
            result = await fetch_url(session, url)
            file.write(json.dumps(result) + '\n')
            queue.task_done()


async def tasks_producer(
    queue: asyncio.Queue, urls: List[str], package_size: int
):
    for package in package_generator(urls, package_size):
        for url in package:
            await queue.put(url)


async def fetch_urls(urls: List[str], file_path: str, package_size: int = 100):
    queue: asyncio.Queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        num_workers = 5
        workers = [
            asyncio.create_task(
                worker(queue, session, file_path)
            ) for _ in range(num_workers)
        ]

        await tasks_producer(queue, urls, package_size)

        for _ in range(num_workers):
            await queue.put(None)

        await asyncio.gather(*workers)

    print(f'Результаты записаны в файл {file_path}')


if __name__ == '__main__':
    urls = [
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url"
    ]
    asyncio.run(fetch_urls(urls, './results.jsonl'))
