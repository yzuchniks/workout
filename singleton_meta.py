from datetime import datetime


class CreatedAtMeta(type):
    def __new__(cls, name, bases, dct):
        dct['created_at_cls'] = datetime.now()
        return super().__new__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        object = super().__call__(*args, **kwargs)
        object.created_at = datetime.now()
        return object


class SingletonMeta(type):
    _objects: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._objects:
            cls._objects[cls] = super().__call__(*args, **kwargs)
        return cls._objects[cls]


class SingletonClass(metaclass=SingletonMeta):
    def __init__(self, value):
        self.value = value


class Singleton:
    _odject = None

    def __new__(cls, *args, **kwargs):
        if not cls._odject:
            cls._odject = super().__new__(cls)
        return cls._odject

    def __init__(self, value):
        self.value = value
