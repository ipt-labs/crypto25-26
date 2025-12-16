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

'''
Завдання 2: Генерація простих чисел
'''

# Визначення необхідної довжини в бітах
PRIME_BIT_LENGTH = 256

# Генерація двох пар простих чисел (p, q) та (p1, q1) для RSA.
def generate_rsa_primes():
    print(f"Генерація простого числа p (довжина {PRIME_BIT_LENGTH} біт)...")
    p = find_prime(PRIME_BIT_LENGTH)
    print(f"Знайдено p: {p}")

    print(f"Генерація простого числа q (довжина {PRIME_BIT_LENGTH} біт)...")
    q = find_prime(PRIME_BIT_LENGTH)
    print(f"Знайдено q: {q}")

    n = p * q

    p1, q1, n1 = 0, 0, 0

    while n1 < n:
        print("\nГенерація простих чисел для Абонента В...")

        p1 = find_prime(PRIME_BIT_LENGTH)
        q1 = find_prime(PRIME_BIT_LENGTH)
        n1 = p1 * q1

        if n1 < n:
            print(f"n1 ({n1}) < n ({n}). Повторна генерація p1, q1.")

    print(f"Знайдено p1: {p1}")
    print(f"Знайдено q1: {q1}")

    print(f"\nПеревірка умови pq <= p1q1: {n} <= {n1} -> {n <= n1}")

    return p, q, p1, q1

# Демонстрація роботи
# try:
#     p_A, q_A, p1_B, q1_B = generate_rsa_primes()
#     print("\n--- Результати генерації 2 завдання ---")
#     print(f"Абонент А: p={p_A}, q={q_A}, n={p_A*q_A}")
#     print(f"Абонент В: p1={p1_B}, q1={q1_B}, n1={p1_B*q1_B}")
# except Exception as e:
#     print(f"Виникла помилка: {e}")

'''
Завдання 3: Генерація ключових пар для RSA
'''

# Розширений алгоритм Евкліда.
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1

    gcd, x1, y1 = extended_gcd(b % a, a)

    x = y1 - (b // a) * x1
    y = x1

    return gcd, x, y

# Знаходження оберненого елемент d до e за модулем phi_n.
def inverse_mod(e, phi_n):
    gcd, x, y = extended_gcd(e, phi_n)

    if gcd != 1:
        raise Exception("Обернений елемент не існує. e та phi(n) не взаємно прості.")
    else:
        return x % phi_n

# Генерує ключову пару RSA для заданих простих чисел p і q.
def GenerateKeyPair(p, q):
    if p == q:
        raise Exception("Числа p та q не можуть співпадати у схемі RSA.")

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Вибір e. Рекомендоване значення e = 2^16 + 1 (65537)
    e = 65537

    gcd_val, _, _ = extended_gcd(e, phi_n)

    if gcd_val != 1:
        raise Exception(f"Обране e={e} не є взаємно простим з phi(n)={phi_n}. gcd={gcd_val}")

    d = inverse_mod(e, phi_n)

    public_key = (n, e)
    private_key = (d, p, q)

    return public_key, private_key

# Демонстрація роботи
# PK_A, SK_A = GenerateKeyPair(p_A, q_A)
# PK_B, SK_B = GenerateKeyPair(p1_B, q1_B)
# print("\n----------------------------------------------")
# print("\n--- Результати генерації 3 завдання ---")
# print(f"Ключі А: PK={PK_A}, SK={SK_A}")
# print(f"Ключі В: PK={PK_B}, SK={SK_B}")
