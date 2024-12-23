# mypy: ignore-errors
import random
import time
import redis


class RateLimitExceed(Exception):
    """Ошибка превышения лимита запросов."""


class RateLimiter:
    def __init__(self, rate_limit=5, time_window=3):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.key = 'api_rate_limiter'

    def test(self):
        '''
        Проверяет, можно ли выполнить запрос в пределах установленного лимита.
        '''
        current_time = int(time.time())

        self.redis.zremrangebyscore(
            self.key,
            0,
            current_time - self.time_window
        )

        request_count = self.redis.zcard(self.key)

        if request_count < self.rate_limit:
            self.redis.zadd(self.key, {str(current_time): current_time})
            return True
        else:
            return False


def make_api_request(rate_limiter):
    if not rate_limiter.test():
        raise RateLimitExceed('Превышен лимит запросов!')
    else:
        print('Запрос к API выполнен')


if __name__ == '__main__':
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print('Превышен лимит запросов!')
        else:
            print('Все в порядке')
