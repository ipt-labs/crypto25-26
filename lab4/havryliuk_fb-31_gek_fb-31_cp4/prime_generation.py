"""
Модуль генерації простих чисел для RSA
Варіант 6
"""

import random
from primality_tests import is_prime


def generate_random_prime(bit_length: int, test_type: str = "miller_rabin") -> int:
    """
    Генерація випадкового простого числа заданої довжини
    
    Args:
        bit_length: довжина числа в бітах (мінімум 8)
        test_type: тип тесту простоти
    
    Returns:
        Просте число заданої довжини
    """
    if bit_length < 8:
        raise ValueError("Довжина має бути мінімум 8 біт")
    
    while True:
        # Генеруємо випадкове число потрібної довжини
        candidate = random.randrange(2**(bit_length - 1), 2**bit_length)
        
        # Робимо непарним
        if candidate % 2 == 0:
            candidate += 1
        
        # Перевіряємо на простоту
        if is_prime(candidate, test_type):
            return candidate


def generate_strong_prime(bit_length: int, test_type: str = "miller_rabin") -> int:
    """
    Генерація "гарного" простого числа p такого, що p-1 має великий простий дільник
    Використовується метод: p = 2*p' + 1, де p' також просте (число Софі Жермен)
    
    Args:
        bit_length: довжина результуючого числа в бітах (мінімум 16)
        test_type: тип тесту простоти
    
    Returns:
        "Гарне" просте число
    """
    if bit_length < 16:
        raise ValueError("Довжина має бути мінімум 16 біт")
    
    max_attempts = 10000
    attempts = 0
    
    while attempts < max_attempts:
        # Генеруємо просте p' на 1 біт менше
        p_prime = generate_random_prime(bit_length - 1, test_type)
        
        # Перевіряємо числа виду p = 2*i*p' + 1 для малих i
        for i in range(1, 100):
            p = 2 * i * p_prime + 1
            
            # Перевіряємо чи не перевищили потрібну довжину
            if p.bit_length() > bit_length:
                break
            
            # Перевіряємо чи p просте
            if is_prime(p, test_type):
                return p
        
        attempts += 1
    
    # Якщо не вдалося згенерувати "гарне" число, повертаємо звичайне просте
    print("Увага: не вдалося згенерувати strong prime, повертаємо звичайне просте")
    return generate_random_prime(bit_length, test_type)


def generate_safe_prime_pair(bit_length: int, test_type: str = "miller_rabin") -> tuple[int, int]:
    """
    Генерація пари простих чисел p, q для RSA
    
    Args:
        bit_length: довжина кожного числа в бітах (результуючий модуль буде ~2*bit_length)
        test_type: тип тесту простоти
    
    Returns:
        (p, q): пара різних простих чисел
    """
    p = generate_strong_prime(bit_length, test_type)
    
    # Генеруємо q відмінне від p
    while True:
        q = generate_strong_prime(bit_length, test_type)
        if q != p:
            break
    
    return p, q


def find_next_prime(start: int, test_type: str = "miller_rabin") -> int:
    """
    Знаходження наступного простого числа після заданого
    
    Args:
        start: початкове число
        test_type: тип тесту простоти
    
    Returns:
        Найменше просте >= start
    """
    candidate = start if start % 2 == 1 else start + 1
    
    while True:
        if is_prime(candidate, test_type):
            return candidate
        candidate += 2
