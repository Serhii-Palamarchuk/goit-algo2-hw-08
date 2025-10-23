"""
Завдання 2. Реалізація Rate Limiter з використанням алгоритму Sliding Window 
для обмеження частоти повідомлень у чаті

Механізм обмеження частоти повідомлень від користувачів для запобігання спаму.
"""

import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    """
    Rate Limiter з використанням алгоритму Sliding Window
    
    Параметри:
    - window_size: розмір часового вікна в секундах
    - max_requests: максимальна кількість повідомлень у вікні
    """
    
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        # Словник для зберігання історії повідомлень кожного користувача
        # Ключ - user_id, значення - deque з часовими мітками повідомлень
        self.user_messages: Dict[str, deque] = {}
    
    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Очищення застарілих запитів з вікна та оновлення активного часового вікна
        
        Параметри:
        - user_id: ідентифікатор користувача
        - current_time: поточний час
        """
        if user_id not in self.user_messages:
            return
        
        # Видаляємо всі повідомлення, старші за window_size
        window_start = current_time - self.window_size
        
        while (self.user_messages[user_id] and 
               self.user_messages[user_id][0] <= window_start):
            self.user_messages[user_id].popleft()
        
        # Якщо у користувача не залишилось повідомлень у вікні, видаляємо його запис
        if not self.user_messages[user_id]:
            del self.user_messages[user_id]
    
    def can_send_message(self, user_id: str) -> bool:
        """
        Перевірка можливості відправлення повідомлення в поточному часовому вікні
        
        Параметри:
        - user_id: ідентифікатор користувача
        
        Повертає:
        - True, якщо повідомлення можна відправити
        - False, якщо ліміт перевищено
        """
        current_time = time.time()
        
        # Очищаємо застарілі повідомлення
        self._cleanup_window(user_id, current_time)
        
        # Якщо користувача немає в словнику або у нього менше max_requests повідомлень
        if user_id not in self.user_messages:
            return True
        
        return len(self.user_messages[user_id]) < self.max_requests
    
    def record_message(self, user_id: str) -> bool:
        """
        Запис нового повідомлення й оновлення історії користувача
        
        Параметри:
        - user_id: ідентифікатор користувача
        
        Повертає:
        - True, якщо повідомлення успішно записано
        - False, якщо ліміт перевищено і повідомлення відхилено
        """
        current_time = time.time()
        
        # Перевіряємо, чи можна відправити повідомлення
        if not self.can_send_message(user_id):
            return False
        
        # Додаємо нове повідомлення
        if user_id not in self.user_messages:
            self.user_messages[user_id] = deque()
        
        self.user_messages[user_id].append(current_time)
        return True
    
    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Розрахунок часу очікування до можливості відправлення наступного повідомлення
        
        Параметри:
        - user_id: ідентифікатор користувача
        
        Повертає:
        - Час очікування в секундах (0, якщо можна відправити зараз)
        """
        current_time = time.time()
        
        # Очищаємо застарілі повідомлення
        self._cleanup_window(user_id, current_time)
        
        # Якщо користувача немає або можна відправити повідомлення
        if user_id not in self.user_messages:
            return 0.0
        
        if len(self.user_messages[user_id]) < self.max_requests:
            return 0.0
        
        # Час, коли найстаріше повідомлення вийде з вікна
        oldest_message_time = self.user_messages[user_id][0]
        time_until_oldest_expires = (oldest_message_time + self.window_size) - current_time
        
        return max(0.0, time_until_oldest_expires)


# Демонстрація роботи
def test_rate_limiter():
    """Тестова функція для демонстрації роботи Rate Limiter"""
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
