'''
Завдання 1: Пошук випадкового простого числа
'''
import random

# Швидке піднесення до степеня за модулем (Схема Горнера).
def modular_exponentiation(base, exponent, modulus):
    result = 1
    base %= modulus

    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus

        base = (base * base) % modulus
        exponent //= 2

    return result

# Тест пробних ділень на малі прості числа.
def trial_division(n, limit=1000):
    if n < 2: return False

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for p in small_primes:
        if n == p:
            return True
        if p >= limit:
            break
        if n % p == 0:
            return False

    return True

# Імовірнісний тест Міллера-Рабіна.
def miller_rabin_test(n, k=40):
    if n < 2: return False
    if n % 2 == 0: return n == 2

    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randint(2, n - 2)

        x = modular_exponentiation(a, d, n)

        # Умова: a^d mod n = 1
        if x == 1 or x == n - 1:
            continue

        is_strong_pseudoprime = False

        # Умова: a^(d * 2^r) mod n = -1 (тобто n-1) для 0 <= r < s
        for r in range(1, s):
            x = modular_exponentiation(x, 2, n)
            if x == n - 1:
                is_strong_pseudoprime = True
                break
            if x == 1:
                return False

        if not is_strong_pseudoprime:
            return False

    return True

# Пошук випадкового простого числа заданої довжини в бітах.
def find_prime(bit_length):
    min_val = 2**(bit_length - 1)
    max_val = 2**bit_length - 1

    start_num = min_val if min_val % 2 != 0 else min_val + 1

    x = random.randint(start_num, max_val)

    if x % 2 == 0:
        x += 1

    num = x
    while num <= max_val:
        if not trial_division(num):
            num += 2
            continue

        if miller_rabin_test(num):
            return num

        num += 2

    # Якщо не знайшли в прямому напрямку, шукаємо в зворотньому (від max_val)
    num = max_val if max_val % 2 != 0 else max_val - 1
    while num >= min_val:
        if not trial_division(num):
            num -= 2
            continue

        if miller_rabin_test(num):
            return num

        num -= 2

    raise Exception("Не вдалося знайти просте число в заданому інтервалі.")
