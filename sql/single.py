# mypy: ignore-errors
import redis
import functools

r = redis.StrictRedis(host='localhost', port=6379, db=0)


def single(max_processing_time):
    '''
    Декоратор который исключает паралельное выполнение функции.
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f'lock:{func.__name__}'

            if r.get(lock_key):
                raise Exception('Функция уже выполняется.')

            if not r.setnx(lock_key, 'locked'):
                raise Exception('Не удалось блокировать функцию, '
                                'возможно она уже заблокирована.')

            r.expire(lock_key, max_processing_time)

            try:
                return func(*args, **kwargs)
            finally:
                r.delete(lock_key)

        return wrapper
    return decorator
