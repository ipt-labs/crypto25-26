import secrets
import random
import sys 
sys.stdout.reconfigure(encoding='utf-8')


# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

def gcd(a, b):
    """Обчислення найбільшого спільного дільника"""
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    """Обчислення оберненого елемента за модулем"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd_val, x, _ = extended_gcd(a % m, m)
    if gcd_val != 1:
        raise ValueError("Обернений елемент не існує")
    return (x % m + m) % m

def mod_exp(base, exp, mod):
    """Швидке піднесення до степеня за модулем"""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp // 2
        base = (base * base) % mod
    return result

# ===== ТЕСТИ НА ПРОСТОТУ (ПУНКТ 1) =====

def trial_division(n):
    """Пробні ділення на малі прості числа"""
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    
    for p in small_primes:
        if n % p == 0:
            return n == p
    return True

def miller_rabin_test(n, k=20):
    """Тест Міллера-Рабіна"""
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записуємо n-1 = d * 2^s
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
        
        for _ in range(s - 1):
            x = mod_exp(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True

def is_prime(n, k=20):
    """Перевірка числа на простоту"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    
    # Пробні ділення
    if not trial_division(n):
        return False
    
    # Тест Міллера-Рабіна
    return miller_rabin_test(n, k)

def generate_prime(bits):
    """Генерація випадкового простого числа заданої довжини (ПУНКТ 1)"""
    while True:
        # Генеруємо випадкове число заданої довжини
        num = secrets.randbits(bits)
        # Встановлюємо старший біт для забезпечення потрібної довжини
        num |= (1 << (bits - 1))
        # Робимо непарним
        num |= 1
        
        if is_prime(num):
            return num

# ===== ФУНКЦІЇ RSA (ПУНКТИ 2-5) =====

def GenerateKeyPair(p, q, e=65537):
    """Генерація ключової пари RSA (ПУНКТ 3)"""
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Перевіряємо, чи e взаємно просте з phi(n)
    if gcd(e, phi) != 1:
        raise ValueError("e не взаємно просте з phi(n)")
    
    d = mod_inverse(e, phi)
    return (e, n), (d, p, q)

def Encrypt(M, public_key):
    """Шифрування повідомлення (ПУНКТ 4)"""
    e, n = public_key
    return mod_exp(M, e, n)

def Decrypt(C, private_key):
    """Розшифрування повідомлення (ПУНКТ 4)"""
    d, n = private_key[0], private_key[1] * private_key[2] if len(private_key) > 2 else private_key[1]
    return mod_exp(C, d, n)

def Sign(M, private_key):
    """Створення цифрового підпису (ПУНКТ 4)"""
    d, n = private_key[0], private_key[1] * private_key[2] if len(private_key) > 2 else private_key[1]
    return mod_exp(M, d, n)

def Verify(M, S, public_key):
    """Перевірка цифрового підпису (ПУНКТ 4)"""
    e, n = public_key
    return M == mod_exp(S, e, n)

def SendKey(k, receiver_public, sender_private):
    """Відправка ключа (ПУНКТ 5)"""
    e1, n1 = receiver_public
    d, n = sender_private[0], sender_private[1] * sender_private[2]
    
    S = Sign(k, sender_private)  # Підписуємо ключ
    k1 = Encrypt(k, receiver_public)  # Шифруємо ключ
    S1 = Encrypt(S, receiver_public)  # Шифруємо підпис
    
    return k1, S1

def ReceiveKey(k1, S1, receiver_private, sender_public):
    """Отримання ключа (ПУНКТ 5)"""
    d1, n1 = receiver_private[0], receiver_private[1] * receiver_private[2]
    e, n = sender_public
    
    k = Decrypt(k1, receiver_private)  # Розшифровуємо ключ
    S = Decrypt(S1, receiver_private)  # Розшифровуємо підпис
    
    # Перевіряємо підпис
    if Verify(k, S, sender_public):
        return k
    else:
        raise ValueError("Підпис не вірний")

# ===== ОСНОВНА ПРОГРАМА =====

def main():
    print("=== ЛАБОРАТОРНА РОБОТА: КРИПТОСИСТЕМА RSA ===\n")
    
    # ПУНКТ 1: Генерація простих чисел
    print("1. ГЕНЕРАЦІЯ ПРОСТИХ ЧИСЕЛ (256 біт)...")
    bits = 256
    
    # Генеруємо пари простих чисел
    p = generate_prime(bits)
    q = generate_prime(bits)
    p1 = generate_prime(bits)
    q1 = generate_prime(bits)
    
    # Переконуємося, що n <= n1 (умова pq ≤ p1q1)
    while p * q > p1 * q1:
        p1 = generate_prime(bits)
        q1 = generate_prime(bits)
    
    print(f"p  = {p}")
    print(f"q  = {q}")
    print(f"p1 = {p1}")
    print(f"q1 = {q1}")
    print(f"Умова pq ≤ p1q1: {p * q <= p1 * q1}")
    print()
    
    # ПУНКТ 3: Генерація ключових пар
    print("3. ГЕНЕРАЦІЯ КЛЮЧОВИХ ПАР...")
    
    # Абонент A
    public_A, private_A = GenerateKeyPair(p, q)
    e, n = public_A
    d, p_val, q_val = private_A
    
    # Абонент B
    public_B, private_B = GenerateKeyPair(p1, q1)
    e1, n1 = public_B
    d1, p1_val, q1_val = private_B
    
    print("Абонент A:")
    print(f"  Відкритий ключ: e = {e}")
    print(f"                 n = {n}")
    print(f"  Закритий ключ: d = {d}")
    print(f"  p = {p_val}")
    print(f"  q = {q_val}")
    print()
    
    print("Абонент B:")
    print(f"  Відкритий ключ: e1 = {e1}")
    print(f"                 n1 = {n1}")
    print(f"  Закритий ключ: d1 = {d1}")
    print(f"  p1 = {p1_val}")
    print(f"  q1 = {q1_val}")
    print()
    
    # ПУНКТ 4: Шифрування, розшифрування та цифровий підпис
    print("4. ШИФРУВАННЯ, РОЗШИФРУВАННЯ ТА ЦИФРОВИЙ ПІДПИС")
    
    # Генеруємо випадкове повідомлення
    M = secrets.randbelow(min(n, n1))
    print(f"Випадкове повідомлення M = {M}")
    print()
    
    # Шифрування для абонента A
    C_A = Encrypt(M, public_A)
    print(f"Шифротекст для A: C = {C_A}")
    
    # Розшифрування для абонента A
    M_decrypted_A = Decrypt(C_A, private_A)
    print(f"Розшифроване повідомлення A: {M_decrypted_A}")
    print(f"Перевірка коректності: {M == M_decrypted_A}")
    print()
    
    # Шифрування для абонента B
    C_B = Encrypt(M, public_B)
    print(f"Шифротекст для B: C1 = {C_B}")
    
    # Розшифрування для абонента B
    M_decrypted_B = Decrypt(C_B, private_B)
    print(f"Розшифроване повідомлення B: {M_decrypted_B}")
    print(f"Перевірка коректності: {M == M_decrypted_B}")
    print()
    
    # Цифровий підпис для абонента A
    S_A = Sign(M, private_A)
    print(f"Цифровий підпис A: S = {S_A}")
    print(f"Перевірка підпису A: {Verify(M, S_A, public_A)}")
    print()
    
    # Цифровий підпис для абонента B
    S_B = Sign(M, private_B)
    print(f"Цифровий підпис B: S1 = {S_B}")
    print(f"Перевірка підпису B: {Verify(M, S_B, public_B)}")
    print()
    
    print("5. ПРОТОКОЛ КОНФІДЕНЦІЙНОГО РОЗСИЛАННЯ КЛЮЧІВ\n")

    # Крок 1: А генерує випадковий ключ k
    k = secrets.randbelow(n)
    print(f"Повідомлення k = {k}\n")

    # Крок 2: А створює цифровий підпис S для k
    S = Sign(k, private_A)
    print(f"А створює цифровий підпис для k: S = {S}\n")

    # Крок 3: А формує повідомлення для B (шифрування)
    k1 = Encrypt(k, public_B)
    S1 = Encrypt(S, public_B)
    print("А формує повідомлення для B:")
    print(f"  Зашифрований ключ (k1) = {k1}")
    print(f"  Зашифрований підпис (S1) = {S1}\n")

    # Крок 4: B отримує повідомлення
    print("B отримує повідомлення від A і розшифровує його:")
    k_received = Decrypt(k1, private_B)
    S_received = Decrypt(S1, private_B)
    print(f"  Розшифрований ключ k = {k_received}")
    print(f"  Розшифрований підпис S = {S_received}\n")

    # Крок 5: B перевіряє підпис за допомогою відкритого ключа A
    auth = Verify(k_received, S_received, public_A)
    print(f"Перевірка цифрового підпису A (автентифікація): {auth}\n")

    # Крок 6: Підсумок
    if auth:
        print(f"Протокол успішно виконано: ключ k = {k_received} отримано конфіденційно та підпис перевірено.")
    else:
        print("Помилка автентифікації: підпис не відповідає повідомленню.")

        
        print("\n=== ВСІ ПУНКТИ ВИКОНАНІ УСПІШНО ===")

if __name__ == "__main__":
    main()