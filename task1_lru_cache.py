"""
Завдання 1. Оптимізація доступу до даних за допомогою LRU-кешу

Реалізація програми, що демонструє, як LRU-кеш пришвидшує 
багаторазові «гарячі» запити до великого масиву чисел.
"""

import random
import time
from typing import Dict, Tuple


class LRUCache:
    """Реалізація LRU (Least Recently Used) кешу"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[Tuple[int, int], int] = {}
        self.access_order = []  # Список для відстеження порядку використання
    
    def get(self, key: Tuple[int, int]) -> int:
        """
        Отримати значення з кешу за ключем.
        Повертає -1, якщо ключ не знайдено (cache-miss).
        """
        if key in self.cache:
            # Оновлюємо порядок доступу
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return -1
    
    def put(self, key: Tuple[int, int], value: int) -> None:
        """Додати значення в кеш"""
        if key in self.cache:
            # Якщо ключ вже є, оновлюємо його позицію
            self.access_order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Якщо кеш переповнено, видаляємо найменш використовуваний елемент
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def invalidate_range(self, index: int) -> None:
        """
        Видалити з кешу всі діапазони, що містять вказаний індекс
        """
        keys_to_remove = []
        for (left, right) in self.cache.keys():
            if left <= index <= right:
                keys_to_remove.append((left, right))
        
        for key in keys_to_remove:
            del self.cache[key]
            self.access_order.remove(key)


# Ініціалізація глобального кешу
cache = LRUCache(capacity=1000)


def range_sum_no_cache(array: list, left: int, right: int) -> int:
    """Обчислити суму елементів array[left:right+1] без кешування"""
    return sum(array[left:right + 1])


def update_no_cache(array: list, index: int, value: int) -> None:
    """Оновити елемент array[index] без кешування"""
    array[index] = value


def range_sum_with_cache(array: list, left: int, right: int) -> int:
    """
    Обчислити суму елементів array[left:right+1] з використанням кешу
    """
    key = (left, right)
    cached_value = cache.get(key)
    
    if cached_value != -1:
        # Cache hit - повертаємо закешоване значення
        return cached_value
    
    # Cache miss - обчислюємо суму, зберігаємо в кеш і повертаємо
    result = sum(array[left:right + 1])
    cache.put(key, result)
    return result


def update_with_cache(array: list, index: int, value: int) -> None:
    """
    Оновити елемент array[index] з інвалідацією кешу
    """
    array[index] = value
    # Видаляємо всі діапазони з кешу, що містять змінений індекс
    cache.invalidate_range(index)


def make_queries(n: int, q: int, hot_pool: int = 30, 
                 p_hot: float = 0.95, p_update: float = 0.03) -> list:
    """
    Генерація масиву запитів для тестування
    
    Параметри:
    - n: розмір масиву
    - q: кількість запитів
    - hot_pool: кількість «гарячих» діапазонів
    - p_hot: ймовірність вибору «гарячого» діапазону
    - p_update: частка запитів на оновлення
    """
    # Створюємо пул «гарячих» діапазонів
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
           for _ in range(hot_pool)]
    
    queries = []
    for _ in range(q):
        if random.random() < p_update:  # ~3% запитів — Update
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:  # ~97% — Range
            if random.random() < p_hot:  # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:  # 5% — випадкові діапазони
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    
    return queries


def test_without_cache(array: list, queries: list) -> float:
    """Тестування без кешу"""
    array_copy = array.copy()
    start_time = time.time()
    
    for query in queries:
        if query[0] == "Update":
            _, idx, val = query
            update_no_cache(array_copy, idx, val)
        else:  # Range
            _, left, right = query
            range_sum_no_cache(array_copy, left, right)
    
    return time.time() - start_time


def test_with_cache(array: list, queries: list) -> float:
    """Тестування з кешем"""
    global cache
    cache = LRUCache(capacity=1000)  # Очищаємо кеш перед тестом
    
    array_copy = array.copy()
    start_time = time.time()
    
    for query in queries:
        if query[0] == "Update":
            _, idx, val = query
            update_with_cache(array_copy, idx, val)
        else:  # Range
            _, left, right = query
            range_sum_with_cache(array_copy, left, right)
    
    return time.time() - start_time


def main():
    """Основна функція для тестування"""
    print("=" * 60)
    print("Тестування LRU-кешу для оптимізації запитів до масиву")
    print("=" * 60)
    
    # Параметри тесту
    n = 100_000  # Розмір масиву
    q = 50_000   # Кількість запитів
    
    print(f"\nПараметри:")
    print(f"  Розмір масиву: {n:,}")
    print(f"  Кількість запитів: {q:,}")
    print(f"  Ємність кешу: 1,000")
    
    # Генерація масиву та запитів
    print("\nГенерація даних...")
    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)
    
    # Підрахунок статистики запитів
    update_count = sum(1 for q in queries if q[0] == "Update")
    range_count = len(queries) - update_count
    
    print(f"\nСтатистика запитів:")
    print(f"  Range запити: {range_count:,} ({range_count/len(queries)*100:.1f}%)")
    print(f"  Update запити: {update_count:,} ({update_count/len(queries)*100:.1f}%)")
    
    # Тестування без кешу
    print("\n" + "-" * 60)
    print("Виконання запитів БЕЗ кешу...")
    time_no_cache = test_without_cache(array, queries)
    
    # Тестування з кешем
    print("Виконання запитів З кешем...")
    time_with_cache = test_with_cache(array, queries)
    
    # Виведення результатів
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТИ:")
    print("=" * 60)
    print(f"Без кешу : {time_no_cache:6.2f} с")
    print(f"LRU-кеш  : {time_with_cache:6.2f} с  "
          f"(прискорення ×{time_no_cache/time_with_cache:.1f})")
    print("=" * 60)
    
    # Додаткова статистика
    speedup = time_no_cache / time_with_cache
    time_saved = time_no_cache - time_with_cache
    efficiency = (time_saved / time_no_cache) * 100
    
    print(f"\nДодаткова статистика:")
    print(f"  Заощаджено часу: {time_saved:.2f} с")
    print(f"  Ефективність: {efficiency:.1f}%")
    print(f"  Прискорення: {speedup:.2f}x")


if __name__ == "__main__":
    main()
