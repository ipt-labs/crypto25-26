"""
Модуль тестів перевірки чисел на простоту
Варіант 6
"""

import random
from arithmetic_ops import fast_power_mod, find_gcd


# Малі прості числа для тесту пробних ділень (перші 50 простих)
SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229
]


def trial_division_test(candidate: int) -> bool:
    """
    Тест пробних ділень - перевірка на поділ малими простими
    
    Args:
        candidate: число для перевірки
    
    Returns:
        True якщо число пройшло тест, False якщо точно складене
    """
    if candidate < 2:
        return False
    
    if candidate == 2:
        return True
        
    if candidate % 2 == 0:
        return False
    
    for prime in SMALL_PRIMES:
        if candidate == prime:
            return True
        if candidate % prime == 0:
            return False
    
    return True


def compute_jacobi_symbol(numerator: int, denominator: int) -> int:
    """
    Обчислення символу Якобі для тесту Соловея-Штрассена
    
    Args:
        numerator: чисельник (a)
        denominator: знаменник (n) - має бути непарним додатним
    
    Returns:
        Символ Якобі (a/n)
    """
    if denominator <= 0 or denominator % 2 == 0:
        raise ValueError("Знаменник має бути додатним непарним числом")
    
    numerator %= denominator
    result = 1
    
    while numerator != 0:
        while numerator % 2 == 0:
            numerator //= 2
            if denominator % 8 in [3, 5]:
                result = -result
        
        numerator, denominator = denominator, numerator
        if numerator % 4 == 3 and denominator % 4 == 3:
            result = -result
        
        numerator %= denominator
    
    if denominator == 1:
        return result
    return 0


def fermat_test(candidate: int, rounds: int = 5) -> bool:
    """
    Тест Ферма на простоту
    
    Args:
        candidate: число для перевірки
        rounds: кількість раундів перевірки
    
    Returns:
        True якщо число ймовірно просте, False якщо точно складене
    """
    if candidate < 2:
        return False
    if candidate == 2 or candidate == 3:
        return True
    if candidate % 2 == 0:
        return False
    
    for _ in range(rounds):
        witness = random.randint(2, candidate - 1)
        
        if find_gcd(witness, candidate) != 1:
            return False
        
        if fast_power_mod(witness, candidate - 1, candidate) != 1:
            return False
    
    return True


def solovay_strassen_test(candidate: int, rounds: int = 5) -> bool:
    """
    Тест Соловея-Штрассена на простоту
    
    Args:
        candidate: число для перевірки
        rounds: кількість раундів перевірки
    
    Returns:
        True якщо число ймовірно просте, False якщо точно складене
    """
    if candidate < 2:
        return False
    if candidate == 2:
        return True
    if candidate % 2 == 0:
        return False
    
    for _ in range(rounds):
        witness = random.randint(2, candidate - 1)
        
        if find_gcd(witness, candidate) != 1:
            return False
        
        jacobi = compute_jacobi_symbol(witness, candidate) % candidate
        power = fast_power_mod(witness, (candidate - 1) // 2, candidate)
        
        if jacobi != power:
            return False
    
    return True


def miller_rabin_test(candidate: int, rounds: int = 8) -> bool:
    """
    Тест Міллера-Рабіна на простоту

    Args:
        candidate: число для перевірки
        rounds: кількість раундів перевірки

    Returns:
        True якщо число ймовірно просте, False якщо точно складене
    """
    if candidate < 2:
        return False
    if candidate == 2 or candidate == 3:
        return True
    if candidate % 2 == 0:
        return False

    # Представлення candidate - 1 = 2^s * d
    s = 0
    d = candidate - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    for _ in range(rounds):
        witness = random.randint(2, candidate - 2)
        
        if find_gcd(witness, candidate) != 1:
            return False
        
        x = fast_power_mod(witness, d, candidate)
        
        if x == 1 or x == candidate - 1:
            continue
        
        is_composite = True
        for _ in range(s - 1):
            x = fast_power_mod(x, 2, candidate)
            if x == candidate - 1:
                is_composite = False
                break
            if x == 1:
                return False
        
        if is_composite:
            return False
    
    return True


def is_prime(candidate: int, test_type: str = "miller_rabin", rounds: int = 8) -> bool:
    """
    Перевірка числа на простоту з використанням обраного тесту
    
    Args:
        candidate: число для перевірки
        test_type: тип тесту ("miller_rabin", "fermat", "solovay_strassen")
        rounds: кількість раундів перевірки
    
    Returns:
        True якщо число ймовірно просте, False якщо складене
    """
    # Спочатку тест пробних ділень
    if not trial_division_test(candidate):
        return False
    
    # Потім обраний імовірнісний тест
    if test_type == "miller_rabin":
        return miller_rabin_test(candidate, rounds)
    elif test_type == "fermat":
        return fermat_test(candidate, rounds)
    elif test_type == "solovay_strassen":
        return solovay_strassen_test(candidate, rounds)
    else:
        raise ValueError(f"Невідомий тип тесту: {test_type}")
