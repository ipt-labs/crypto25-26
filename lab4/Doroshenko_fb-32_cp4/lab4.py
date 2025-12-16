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

# Демонстрація роботи 2 завдання
try:
    p_A, q_A, p1_B, q1_B = generate_rsa_primes()
    print("\n--- Результати 2 завдання ---")
    print(f"Абонент А: p={p_A}, q={q_A}, n={p_A*q_A}")
    print(f"Абонент В: p1={p1_B}, q1={q1_B}, n1={p1_B*q1_B}")
except Exception as e:
    print(f"Виникла помилка: {e}")

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

# Демонстрація роботи 3 завдання
PK_A, SK_A = GenerateKeyPair(p_A, q_A)
PK_B, SK_B = GenerateKeyPair(p1_B, q1_B)
print("\n----------------------------------------------")
print("\n--- Результати 3 завдання ---")
print(f"Ключі А: PK={PK_A}, SK={SK_A}")
print(f"Ключі В: PK={PK_B}, SK={SK_B}")

'''
Завдання 4: Шифрування, Розшифрування та Цифровий підпис RSA
'''

import hashlib
import random

# Імітація геш-функції H(M) = m.
def hash_message(M):
    # Перетворення повідомлення M на байти і обчислюємо SHA-256
    if isinstance(M, str):
        M_bytes = M.encode('utf-8')
    elif isinstance(M, int):
        M_bytes = M.to_bytes((M.bit_length() + 7) // 8, byteorder='big')
    else:
        raise TypeError("Повідомлення повинно бути рядком або цілим числом.")

    hash_digest = hashlib.sha256(M_bytes).digest()

    return int.from_bytes(hash_digest, byteorder='big')

# Шифрування повідомлення M за допомогою відкритого ключа (n, e).
def Encrypt(M, public_key):
    n, e = public_key
    if M >= n:
        raise ValueError("Повідомлення M повинно бути менше за модуль n.")

    C = modular_exponentiation(M, e, n)
    return C

# Розшифрування криптограми C за допомогою секретного ключа (d, p, q).
def Decrypt(C, private_key):
    d, p, q = private_key
    n = p * q

    M = modular_exponentiation(C, d, n)
    return M

# Створення цифрового підпису S для повідомлення M.
def Sign(M, private_key):
    d, p, q = private_key
    n = p * q

    # 1. Обчислення геш повідомлення
    m = hash_message(M)
    m_mod_n = m % n

    # 2. Шифрування геш на секретному ключі
    S = modular_exponentiation(m_mod_n, d, n)
    return S

# Перевірка цифрового підпису S для повідомлення M.
def Verify(M, S, public_key):
    n, e = public_key

    # 1. Розшифрування підписа за допомогою відкритого ключа
    m_prime = modular_exponentiation(S, e, n)

    # 2. Обчислення очікуваного геш повідомлення
    m = hash_message(M)
    m_mod_n = m % n

    is_valid = m_prime == m_mod_n

    return is_valid, m_prime, m_mod_n

# Демонстрація роботи 4 завдання
print("\n----------------------------------------------")
print("\n--- Результати 4 завдання ---")
M_INT = 123456789012345
M_STR = "Абонент А підписує це повідомлення."

# Шифрування/Розшифрування (А -> В)
print("\n--- Шифрування та Розшифрування ---")
C_to_B = Encrypt(M_INT, PK_B)
M_decrypted = Decrypt(C_to_B, SK_B)
print(f"ВТ (M): {M_INT}")
print(f"ШТ (C): {C_to_B}")
print(f"Розшифр. M': {M_decrypted}")
print(f"Перевірка розшифр.: {M_decrypted == M_INT}")

# Цифровий Підпис (А)
print("\n--- Цифровий Підпис та Перевірка (Абонент А) ---")
m_hash = hash_message(M_STR) % PK_A[0]
S_A = Sign(M_STR, SK_A)

is_valid_A, m_prime_A, m_A = Verify(M_STR, S_A, PK_A)

print(f"Повідомлення (M): '{M_STR}'")
print(f"Геш H(M) mod n: {m_A}")
print(f"Підпис (S): {S_A}")
print(f"Відновлений Геш (S^e mod n): {m_prime_A}")
print(f"Перевірка підпису: {is_valid_A}")
