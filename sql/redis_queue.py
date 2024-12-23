# mypy: ignore-errors
import redis
import json


class RedisQueue:
    def __init__(
            self,
            queue_name: str,
            host: str = 'localhost',
            port: int = 6379,
            db: int = 0
    ):
        self.redis = redis.StrictRedis(host=host, port=port, db=db)
        self.queue_name = queue_name

    def publish(self, msg: dict):
        '''Публикует сообщение в очередь.'''
        msg_json = json.dumps(msg)
        self.redis.lpush(self.queue_name, msg_json)

    def consume(self) -> dict:
        '''Извлекает сообщение из очереди.'''
        msg_json = self.redis.rpop(self.queue_name)

        if msg_json is None:
            return None

        return json.loads(msg_json)


if __name__ == '__main__':
    q = RedisQueue('my_queue')

    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}
    assert q.consume() is None
