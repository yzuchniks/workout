import json
import math
import random
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Process, Queue, cpu_count


def generate_data(n: int) -> list[int]:
    return [random.randint(1, 1000) for _ in range(n)]


def process_number(number: int) -> int:
    return math.factorial(number)


def with_thread_pool(data: list[int]) -> list[int]:
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_number, data))
    return results


def with_multiprocessing_pool(data: list[int]) -> list[int]:
    with Pool(cpu_count()) as pool:
        results = pool.map(process_number, data)
    return results


def worker(chunk: list[int], output: Queue):
    results = [process_number(num) for num in chunk]
    output.put(results)


def with_multiprocessing_process(data: list[int]) -> list[int]:
    num_processes = cpu_count()
    chunk_size = len(data) // num_processes
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    remainder = len(data) % num_processes
    for i in range(remainder):
        chunks[i].append(data[chunk_size * num_processes + i])
    output: Queue[list[int]] = Queue()
    processes = []

    for chunk in chunks:
        process = Process(target=worker, args=(chunk, output))
        processes.append(process)
        process.start()

    results = []
    for _ in processes:
        results.extend(output.get())

    for process in processes:
        process.join()

    return results


def with_one_stream(data: list[int]) -> list[int]:
    return [process_number(num) for num in data]


def measure_time(func, data):
    start_time = time.time()
    result = func(data)
    elapsed_time = time.time() - start_time
    return result, elapsed_time


def save_results(results: list[int], file_path: str):
    with open(file_path, 'w') as file:
        json.dump(results, file)


if __name__ == '__main__':
    data = generate_data(100000)

    methods = {
        "Однопоточная обработка": with_one_stream,
        "ThreadPoolExecutor": with_thread_pool,
        "multiprocessing.Pool": with_multiprocessing_pool,
        "multiprocessing.Process": with_multiprocessing_process,
    }

    results_table = []
    for method_name, method in methods.items():
        print(f"Запуск метода: {method_name}")
        results, elapsed_time = measure_time(method, data)
        results_table.append((method_name, elapsed_time))
        save_results(results, f'results_{method_name}.json')

    print("\nСравнение производительности:")
    print(f"{'Метод':<30} {'Время (с)'}")
    for method_name, elapsed_time in results_table:
        print(f"{method_name:<30} {elapsed_time:.2f}")
