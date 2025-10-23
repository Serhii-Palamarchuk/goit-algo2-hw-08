# Інструкція з використання

## Швидкий старт

### Запуск завдання 1 (LRU-кеш)

```bash
python task1_lru_cache.py
```

**Очікуваний вихід:**

```
============================================================
Тестування LRU-кешу для оптимізації запитів до масиву
============================================================

Параметри:
  Розмір масиву: 100,000
  Кількість запитів: 50,000
  Ємність кешу: 1,000

...

============================================================
РЕЗУЛЬТАТИ:
============================================================
Без кешу :   9.53 с
LRU-кеш  :   3.15 с  (прискорення ×3.0)
============================================================
```

### Запуск завдання 2 (Rate Limiter)

```bash
python task2_rate_limiter.py
```

**Очікуваний вихід:**

```
=== Симуляція потоку повідомлень ===
Повідомлення  1 | Користувач 2 | ✓
Повідомлення  2 | Користувач 3 | ✓
...
Повідомлення  6 | Користувач 2 | × (очікування 6.9с)
...
```

### Запуск всіх тестів

```bash
python test_all.py
```

Цей файл запустить всі тести для обох завдань з детальними поясненнями.

---

## Використання у власному коді

### Приклад 1: Використання LRU-кешу

```python
from task1_lru_cache import LRUCache

# Створюємо кеш на 100 елементів
cache = LRUCache(capacity=100)

# Додаємо дані
cache.put(("user123", "profile"), {"name": "John", "age": 30})
cache.put(("user456", "profile"), {"name": "Jane", "age": 25})

# Отримуємо дані
result = cache.get(("user123", "profile"))
if result != -1:
    print(f"Cache hit: {result}")
else:
    print("Cache miss - потрібно завантажити з БД")

# Інвалідація
cache.invalidate_range("user123")
```

### Приклад 2: Використання Rate Limiter

```python
from task2_rate_limiter import SlidingWindowRateLimiter

# Створюємо limiter: 5 запитів за 60 секунд
limiter = SlidingWindowRateLimiter(window_size=60, max_requests=5)

def handle_api_request(user_id, request_data):
    # Перевіряємо, чи може користувач зробити запит
    if not limiter.can_send_message(user_id):
        wait_time = limiter.time_until_next_allowed(user_id)
        return {
            "error": "Rate limit exceeded",
            "retry_after": wait_time
        }

    # Записуємо запит
    limiter.record_message(user_id)

    # Обробляємо запит
    return process_request(request_data)
```

### Приклад 3: Кешування результатів функції

```python
from task1_lru_cache import LRUCache
import time

# Кеш для результатів обчислень
computation_cache = LRUCache(capacity=1000)

def expensive_computation(x, y):
    """Коштовна функція, результат якої хочемо кешувати"""
    key = (x, y)

    # Спробуємо отримати з кешу
    cached = computation_cache.get(key)
    if cached != -1:
        return cached

    # Виконуємо обчислення
    time.sleep(1)  # Імітація складних обчислень
    result = x ** 2 + y ** 2

    # Зберігаємо в кеш
    computation_cache.put(key, result)

    return result

# Перший виклик - обчислення займе час
result1 = expensive_computation(10, 20)  # ~1 секунда

# Другий виклик - миттєво з кешу
result2 = expensive_computation(10, 20)  # ~0 секунд
```

### Приклад 4: Захист чат-системи від спаму

```python
from task2_rate_limiter import SlidingWindowRateLimiter

# Різні обмеження для різних типів дій
message_limiter = SlidingWindowRateLimiter(window_size=10, max_requests=5)
image_limiter = SlidingWindowRateLimiter(window_size=60, max_requests=2)

def send_message(user_id, message_type, content):
    # Вибираємо відповідний limiter
    limiter = image_limiter if message_type == "image" else message_limiter

    # Перевіряємо ліміт
    if not limiter.record_message(user_id):
        wait_time = limiter.time_until_next_allowed(user_id)
        return {
            "success": False,
            "error": f"Too many {message_type} messages",
            "wait_seconds": wait_time
        }

    # Відправляємо повідомлення
    return {
        "success": True,
        "message_id": save_message(user_id, content)
    }
```

---

## Налаштування параметрів

### LRU-кеш

```python
# Малий кеш для обмеженої пам'яті
cache = LRUCache(capacity=100)

# Великий кеш для максимальної продуктивності
cache = LRUCache(capacity=10000)

# Середній кеш (рекомендовано)
cache = LRUCache(capacity=1000)
```

**Як обрати розмір кешу:**

- Більший кеш = більше пам'яті, менше cache-miss
- Менший кеш = менше пам'яті, більше cache-miss
- Оптимальний розмір залежить від кількості унікальних запитів

### Rate Limiter

```python
# Дуже обмежувальний (захист від спаму)
limiter = SlidingWindowRateLimiter(window_size=60, max_requests=1)

# Помірний (нормальне використання)
limiter = SlidingWindowRateLimiter(window_size=10, max_requests=5)

# М'який (для авторизованих користувачів)
limiter = SlidingWindowRateLimiter(window_size=60, max_requests=100)
```

**Рекомендації:**

- API endpoints: 100 запитів / 60 секунд
- Відправлення повідомлень: 5 повідомлень / 10 секунд
- Завантаження файлів: 2 файли / 60 секунд
- Аутентифікація: 5 спроб / 300 секунд

---

## Вимірювання продуктивності

### Тестування різних параметрів кешу

```python
from task1_lru_cache import LRUCache, test_with_cache, make_queries
import random
import time

def benchmark_cache_size():
    n = 100_000
    q = 50_000
    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    cache_sizes = [100, 500, 1000, 5000, 10000]

    for size in cache_sizes:
        global cache
        cache = LRUCache(capacity=size)

        exec_time = test_with_cache(array, queries)
        print(f"Розмір кешу: {size:5d} | Час: {exec_time:.2f}с")

benchmark_cache_size()
```

### Моніторинг Rate Limiter

```python
from task2_rate_limiter import SlidingWindowRateLimiter

limiter = SlidingWindowRateLimiter(window_size=10, max_requests=5)

def get_limiter_stats(user_id):
    """Отримати статистику для користувача"""
    current_time = time.time()
    limiter._cleanup_window(user_id, current_time)

    if user_id in limiter.user_messages:
        messages = limiter.user_messages[user_id]
        return {
            "total_messages": len(messages),
            "can_send": limiter.can_send_message(user_id),
            "wait_time": limiter.time_until_next_allowed(user_id),
            "window_start": messages[0] if messages else None,
            "window_end": messages[-1] if messages else None
        }
    return {"total_messages": 0, "can_send": True}

# Використання
stats = get_limiter_stats("user123")
print(f"Користувач може відправити: {stats['can_send']}")
print(f"Повідомлень у вікні: {stats['total_messages']}")
```

---

## Тестування

### Unit тести

Створіть файл `test_unit.py`:

```python
import unittest
from task1_lru_cache import LRUCache
from task2_rate_limiter import SlidingWindowRateLimiter
import time

class TestLRUCache(unittest.TestCase):
    def test_basic_put_get(self):
        cache = LRUCache(capacity=2)
        cache.put((1, 2), 100)
        self.assertEqual(cache.get((1, 2)), 100)

    def test_capacity_limit(self):
        cache = LRUCache(capacity=2)
        cache.put((1, 2), 100)
        cache.put((3, 4), 200)
        cache.put((5, 6), 300)

        # Перший елемент має бути видалений
        self.assertEqual(cache.get((1, 2)), -1)

    def test_invalidation(self):
        cache = LRUCache(capacity=10)
        cache.put((0, 10), 100)
        cache.invalidate_range(5)
        self.assertEqual(cache.get((0, 10)), -1)

class TestRateLimiter(unittest.TestCase):
    def test_first_message(self):
        limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)
        result = limiter.record_message("user1")
        self.assertTrue(result)

    def test_rate_limit(self):
        limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)
        limiter.record_message("user1")

        # Друге повідомлення має бути відхилено
        result = limiter.record_message("user1")
        self.assertFalse(result)

    def test_window_expiry(self):
        limiter = SlidingWindowRateLimiter(window_size=1, max_requests=1)
        limiter.record_message("user1")

        time.sleep(1.5)

        # Після закінчення вікна має дозволитись
        result = limiter.record_message("user1")
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
```

Запуск:

```bash
python test_unit.py
```

---

## Часті запитання (FAQ)

### Питання по LRU-кешу

**Q: Чому використовується список замість OrderedDict?**

A: Для простоти реалізації та прозорості коду. У продакшені можна використати OrderedDict для O(1) операцій.

**Q: Як очистити весь кеш?**

A: Створіть новий екземпляр кешу або додайте метод `clear()`:

```python
def clear(self):
    self.cache.clear()
    self.access_order.clear()
```

**Q: Чи можна зробити кеш thread-safe?**

A: Так, додайте threading.Lock:

```python
import threading

class ThreadSafeLRUCache(LRUCache):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            return super().get(key)

    def put(self, key, value):
        with self.lock:
            super().put(key, value)
```

### Питання по Rate Limiter

**Q: Як обмежити глобально всі запити?**

A: Використовуйте спеціальний user_id для глобальних лімітів:

```python
limiter = SlidingWindowRateLimiter(window_size=60, max_requests=1000)

def handle_request(user_id, request):
    # Перевіряємо і глобальний, і персональний ліміт
    if not limiter.can_send_message("_global_"):
        return "Server overload"
    if not limiter.record_message(user_id):
        return "User rate limit exceeded"

    limiter.record_message("_global_")
    return process_request(request)
```

**Q: Як зберігати дані між перезапусками?**

A: Використовуйте Redis або базу даних:

```python
import redis

class PersistentRateLimiter:
    def __init__(self, redis_client, window_size=10, max_requests=1):
        self.redis = redis_client
        self.window_size = window_size
        self.max_requests = max_requests

    def record_message(self, user_id):
        key = f"rate_limit:{user_id}"
        current_time = time.time()

        # Додаємо запис з TTL
        pipe = self.redis.pipeline()
        pipe.zadd(key, {current_time: current_time})
        pipe.zremrangebyscore(key, 0, current_time - self.window_size)
        pipe.zcard(key)
        pipe.expire(key, self.window_size)

        _, _, count, _ = pipe.execute()

        return count <= self.max_requests
```

---

## Додаткові ресурси

- [LRU Cache на Wikipedia](<https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)>)
- [Rate Limiting Strategies](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Python collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)

---

**Успішної роботи з алгоритмами оптимізації! 🚀**
