import secrets
import random
import sys

# Щоб коректно друкувались укр. символи в консолі Windows
sys.stdout.reconfigure(encoding='utf-8')

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

def gcd(a: int, b: int) -> int:
    """Обчислення найбільшого спільного дільника (НСД)"""
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a: int, m: int) -> int:
    """Обчислення оберненого елемента a^{-1} mod m"""

    def extended_gcd(a: int, b: int):
        if a == 0:
            return b, 0, 1
        g, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return g, x, y

    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError("Обернений елемент не існує (gcd != 1)")
    # Приводимо до додатного представлення
    return (x % m + m) % m

def mod_exp(base: int, exp: int, mod: int) -> int:
    """Швидке піднесення до степеня за модулем (binary exponentiation)"""
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        exp >>= 1
        base = (base * base) % mod
    return result

# ===== ТЕСТИ НА ПРОСТОТУ (ПУНКТ 1) =====

def trial_division(n: int) -> bool:
    """Пробні ділення на малі прості числа"""
    small_primes = [
        2, 3, 5, 7, 11, 13, 17, 19, 23,
        29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71
    ]
    for p in small_primes:
        if n % p == 0:
            return n == p
    return True

def miller_rabin_test(n: int, k: int = 20) -> bool:
    """Ймовірнісний тест Міллера–Рабіна"""
    if n in (2, 3):
        return True
    if n < 2 or n % 2 == 0:
        return False

    # n - 1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = mod_exp(a, d, n)

        if x == 1 or x == n - 1:
            continue

        is_composite = True
        for _ in range(s - 1):
            x = mod_exp(x, 2, n)
            if x == n - 1:
                is_composite = False
                break
        if is_composite:
            return False

    return True

def is_prime(n: int, k: int = 20) -> bool:
    """Перевірка числа на простоту: пробні ділення + Міллер–Рабін"""
    if n < 2:
        return False
    if n in (2, 3):
        return True

    if not trial_division(n):
        return False

    return miller_rabin_test(n, k)

def generate_prime(bits: int) -> int:
    """Генерація випадкового простого числа заданої довжини (bits)"""
    while True:
        # Випадкове число заданої бітової довжини
        num = secrets.randbits(bits)
        # Ставимо старший біт, щоб точно було bits
        num |= (1 << (bits - 1))
        # Робимо непарним
        num |= 1

        if is_prime(num):
            return num

# ===== ФУНКЦІЇ RSA (ПУНКТИ 2–5) =====

def GenerateKeyPair(p: int, q: int, e: int = 65537):
    """Генерація ключової пари RSA для заданих p, q і e"""
    n = p * q
    phi = (p - 1) * (q - 1)

    if gcd(e, phi) != 1:
        raise ValueError("e не є взаємно простим з φ(n)")

    d = mod_inverse(e, phi)
    # Повертаємо (e, n) та (d, p, q)
    return (e, n), (d, p, q)

def Encrypt(M: int, public_key) -> int:
    """Шифрування повідомлення M відкритим ключем (e, n)"""
    e, n = public_key
    return mod_exp(M, e, n)

def Decrypt(C: int, private_key) -> int:
    """Розшифрування шифртексту C секретним ключем (d, p, q) або (d, n)"""
    d = private_key[0]
    if len(private_key) > 2:
        n = private_key[1] * private_key[2]
    else:
        n = private_key[1]
    return mod_exp(C, d, n)

def Sign(M: int, private_key) -> int:
    """Створення цифрового підпису S = M^d mod n"""
    d = private_key[0]
    if len(private_key) > 2:
        n = private_key[1] * private_key[2]
    else:
        n = private_key[1]
    return mod_exp(M, d, n)

def Verify(M: int, S: int, public_key) -> bool:
    """Перевірка цифрового підпису: M ?= S^e mod n"""
    e, n = public_key
    return M == mod_exp(S, e, n)

def SendKey(k: int, receiver_public, sender_private):
    """Відправка ключа k від A до B: повертає (k1, S1)"""
    # k1 = k^e_B mod n_B
    k1 = Encrypt(k, receiver_public)
    # S  = k^d_A mod n_A (підпис)
    S = Sign(k, sender_private)
    # S1 = S^e_B mod n_B
    S1 = Encrypt(S, receiver_public)
    return k1, S1

def ReceiveKey(k1: int, S1: int, receiver_private, sender_public):
    """Отримання ключа B від A: повертає (k_rec, ok)"""
    # Розшифровуємо k та S секретним ключем B
    k_rec = Decrypt(k1, receiver_private)
    S_rec = Decrypt(S1, receiver_private)
    ok = Verify(k_rec, S_rec, sender_public)
    return k_rec, ok

# ===== ОСНОВНА ПРОГРАМА =====

def main():
    # --- Завдання 1: генерація простих ---
    print('=== Завдання 1: генерація простих ===')

    # Просте з інтервалу [1, 500]
    prime_in_range = None
    for x in range(2, 501):
        if is_prime(x):
            prime_in_range = x
            break

    print(f'Просте з інтервалу [1, 500]: {prime_in_range}')

    # Просте 64-бітне число
    prime_64 = generate_prime(64)
    print(f'Просте 64-бітне число: {prime_64}')
    print('=====================================\n')

    # --- Завдання 2: дві пари простих p, q і p1, q1 ---
    print('=== Завдання 2: дві пари простих p,q і p1,q1 ===')
    bits = 256

    p = generate_prime(bits)
    q = generate_prime(bits)
    p1 = generate_prime(bits)
    q1 = generate_prime(bits)

    # умова pq ≤ p1q1
    while p * q > p1 * q1:
        p1 = generate_prime(bits)
        q1 = generate_prime(bits)

    n = p * q
    n1 = p1 * q1

    print(f'p  = {p}')
    print(f'q  = {q}')
    print(f'p1 = {p1}')
    print(f'q1 = {q1}\n')

    print(f'p*q  = {n}')
    print(f'p1*q1 = {n1}\n')
    print(f'Умова pq ≤ p1q1 виконана: {n <= n1}')
    print('=====================================\n')

    # --- Завдання 3–4: RSA для A і B ---
    print('=== Завдання 3–4: RSA для A і B ===')

    # Ключі для A
    public_A, private_A = GenerateKeyPair(p, q)
    e, n = public_A
    d, p_val, q_val = private_A

    # Ключі для B
    public_B, private_B = GenerateKeyPair(p1, q1)
    e1, n1 = public_B
    d1, p1_val, q1_val = private_B

    # Випадкове повідомлення (не більше мінімального модуля)
    M = secrets.randbelow(min(n, n1))
    print(f'Відкрите повідомлення M: {M}')

    # Шифрування/розшифрування для A
    C_A = Encrypt(M, public_A)
    M_dec_A = Decrypt(C_A, private_A)

    print(f'Криптограма для A: {C_A}')
    print(f'Розшифроване A: {M_dec_A}')

    # Шифрування/розшифрування для B
    C_B = Encrypt(M, public_B)
    M_dec_B = Decrypt(C_B, private_B)

    print(f'Криптограма для B: {C_B}')
    print(f'Розшифроване B: {M_dec_B}')

    # Цифровий підпис від A
    S_A = Sign(M, private_A)
    ok_sig_A = Verify(M, S_A, public_A)

    print(f'Цифровий підпис від A: {S_A}')
    print(f'Перевірка підпису A: {"Дійсний" if ok_sig_A else "Недійсний"}')
    print('=====================================\n')

    # --- Завдання 5: протокол розсилання ключа ---
    print('=== Завдання 5: протокол розсилання ключа ===')

    k = secrets.randbelow(n)  # випадковий ключ
    print(f'Випадковий ключ k: {k}\n')

    k1, S1 = SendKey(k, public_B, private_A)
    print('Відправлені значення від A до B:')
    print(f'k1 = {k1}')
    print(f'S1 = {S1}\n')

    k_rec, ok_k = ReceiveKey(k1, S1, private_B, public_A)
    print(f'B відновив ключ k_rec: {k_rec}')
    print(f'Перевірка підпису A: {"Дійсний" if ok_k else "Недійсний"}')
    print('=====================================\n')

    # --- Перевірка через сайт dCode (RSA Cipher) ---
    print('=== Перевірка через сайт dCode (RSA Cipher) для абонента A ===')
    print('Використовуємо значення, які вже обчислені програмою:')
    print(f'M  (відкрите повідомлення) = {M}')
    print(f'C  (криптограма для A)     = {C_A}')
    print(f'n  (модуль)                = {n}')
    print(f'e  (публічний показник)    = {e}')
    print(f'd  (секретний показник)    = {d}\n')

    print('Як підставляти на https://dcode.fr/rsa-cipher :')
    print('  Value of the cipher message (Integer) C = C  (криптограма для A)')
    print('  Public key value (Integer) N            = n')
    print('  Public key value (Integer) E            = e')
    print('  Private key value (Integer) D           = d')
    print("  DISPLAY → 'Plaintext as integer number'")
    print('  Натиснувши CALCULATE/DECRYPT → результат має дорівнювати M.\n')

    print('Ті ж самі значення у шістнадцятковому форматі (для зручності):')
    print(f'n_hex = {hex(n)[2:].upper()}')
    print(f'd_hex = {hex(d)[2:].upper()}')
    print(f'C_hex = {hex(C_A)[2:].upper()}')
    print(f'M_hex = {hex(M)[2:].upper()}')
    print('=====================================')


if __name__ == '__main__':
    main()
