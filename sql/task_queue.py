# mypy: ignore-errors
import environ
from sqlalchemy import (create_engine, Column, Integer,
                        String, Text, DateTime, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

env = environ.Env()
environ.Env.read_env()

DB = env('DB')
USER = env('USER')
PASSWORD = env('PASSWORD')
HOST = env('HOST')
PORT = env.int('PORT', default=5432)
DATABASE = env('DATABASE')

DATABASE_URL = f'{DB}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

Base = declarative_base()

PENDING = 'pending'
PROCESSING = 'processing'
COMPLETED = 'completed'


class TaskQueue(Base):
    """Модель таблицы задач."""
    __tablename__ = 'task_queue'

    id = Column(Integer, primary_key=True)
    task_name = Column(Text, nullable=False)
    status = Column(String(20), default=PENDING)
    worker_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


def fetch_task(worker_id):
    """Получение задачи для воркера."""
    session = Session()
    try:
        task = (
            session.query(TaskQueue)
            .filter(TaskQueue.status == PENDING)
            .with_for_update(skip_locked=True)
            .first()
        )
        if task:
            task.status = PROCESSING
            task.worker_id = worker_id
            session.commit()
            return task
        return None
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def complete_task(task_id):
    """Обновление статуса задачи на 'completed'."""
    session = Session()
    try:
        task = session.query(TaskQueue).get(task_id)
        if task:
            task.status = COMPLETED
            session.commit()
            print(f'Задача {task.id} завершена')
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def process_task(worker_id):
    """Обработка задач воркером."""
    while True:
        task = fetch_task(worker_id)
        if task:
            print(f'Воркер {worker_id} обрабатывает задачу '
                  f'{task.task_name} (ID: {task.id})')
            import time
            time.sleep(2)
            complete_task(task.id)
        else:
            print(f'Воркер {worker_id}: Нет доступных задач')
            break


if __name__ == '__main__':
    worker_id = 1
    process_task(worker_id)
