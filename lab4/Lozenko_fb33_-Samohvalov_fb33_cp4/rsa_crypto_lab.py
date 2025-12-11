import random
import math
from typing import Tuple, Optional



def gcd(a: int, b: int) -> int:
    """Алгоритм Евкліда для знаходження НСД"""
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Розширений алгоритм Евкліда: повертає (gcd, x, y) де ax + by = gcd"""
    if a == 0:
        return b, 0, 1
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd_val, x, y

def mod_inverse(e: int, phi: int) -> int:
    """Знаходить обернений елемент e за модулем phi"""
    gcd_val, x, _ = extended_gcd(e, phi)
    if gcd_val != 1:
        raise ValueError("Обернений елемент не існує")
    return x % phi

def power_mod(base: int, exp: int, mod: int) -> int:
    """Швидке піднесення до степеня за модулем (схема Горнера)"""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result

def jacobi_symbol(a: int, n: int) -> int:
    """Обчислення символу Якобі"""
    if n <= 0 or n % 2 == 0:
        raise ValueError("n має бути непарним додатним числом")
    
    a = a % n
    result = 1
    
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in [3, 5]:
                result = -result
        
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n
    
    return result if n == 1 else 0

# ============================================================================
# ТЕСТИ ПЕРЕВІРКИ НА ПРОСТОТУ
# ============================================================================

def trial_division(n: int, limit: int = 1000) -> bool:
    """Тест пробних ділень на малі прості числа"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 
                    53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False
    
    i = 101
    while i * i <= n and i <= limit:
        if n % i == 0:
            return False
        i += 2
    
    return True

def miller_rabin_test(n: int, k: int = 10) -> bool:
    """Тест Міллера-Рабіна на простоту з k раундами"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Розклад n-1 = 2^s * d
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # k раундів тестування
    for _ in range(k):
        a = random.randrange(2, n - 1)
        
        # Перевірка gcd(a, n)
        if gcd(a, n) != 1:
            return False
        
        # Перевірка чи n сильно псевдопросте за основою a
        x = power_mod(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        is_composite = True
        for _ in range(s - 1):
            x = power_mod(x, 2, n)
            if x == n - 1:
                is_composite = False
                break
        
        if is_composite:
            return False
    
    return True

def is_prime(n: int, k: int = 10) -> bool:
    """Комбінований тест: пробні ділення + Міллер-Рабін"""
    if not trial_division(n):
        return False
    return miller_rabin_test(n, k)

# ============================================================================
# ГЕНЕРАЦІЯ ПРОСТИХ ЧИСЕЛ
# ============================================================================

def generate_prime(bits: int) -> int:
    """Генерує випадкове просте число заданої довжини в бітах"""
    while True:
        # Генеруємо випадкове непарне число
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1  # Встановлюємо старший та молодший біти
        
        if is_prime(n):
            return n

def generate_prime_pair(bits: int) -> Tuple[int, int]:
    """Генерує пару простих чисел p, q таких що p != q"""
    p = generate_prime(bits)
    q = generate_prime(bits)
    
    while q == p:
        q = generate_prime(bits)
    
    return p, q

# ============================================================================
# ГЕНЕРАЦІЯ КЛЮЧІВ RSA
# ============================================================================

def GenerateKeyPair(bits: int = 256) -> Tuple[Tuple[int, int], Tuple[int, int, int]]:
    """
    Генерує пару ключів RSA
    Повертає: ((n, e), (d, p, q))
    """
    # Генеруємо два простих числа
    p, q = generate_prime_pair(bits)
    
    # Обчислюємо модуль
    n = p * q
    
    # Обчислюємо функцію Ойлера
    phi = (p - 1) * (q - 1)
    
    # Вибираємо e (зазвичай 65537)
    e = 65537
    if gcd(e, phi) != 1:
        # Якщо 65537 не підходить, шукаємо інше
        e = 3
        while gcd(e, phi) != 1:
            e += 2
    
    # Знаходимо d - обернений до e за модулем phi
    d = mod_inverse(e, phi)
    
    public_key = (n, e)
    private_key = (d, p, q)
    
    return public_key, private_key

# ============================================================================
# ШИФРУВАННЯ ТА РОЗШИФРУВАННЯ
# ============================================================================

def Encrypt(message: int, public_key: Tuple[int, int]) -> int:
    """Шифрує повідомлення відкритим ключем"""
    n, e = public_key
    if message >= n:
        raise ValueError("Повідомлення занадто велике для даного модуля")
    return power_mod(message, e, n)

def Decrypt(ciphertext: int, private_key: Tuple[int, int, int]) -> int:
    """Розшифровує криптограму секретним ключем"""
    d, p, q = private_key
    n = p * q
    return power_mod(ciphertext, d, n)

# ============================================================================
# ЦИФРОВИЙ ПІДПИС
# ============================================================================

def Sign(message: int, private_key: Tuple[int, int, int]) -> int:
    """Створює цифровий підпис повідомлення"""
    d, p, q = private_key
    n = p * q
    if message >= n:
        raise ValueError("Повідомлення занадто велике для підпису")
    return power_mod(message, d, n)

def Verify(message: int, signature: int, public_key: Tuple[int, int]) -> bool:
    """Перевіряє цифровий підпис"""
    n, e = public_key
    verified_message = power_mod(signature, e, n)
    return verified_message == message

# ============================================================================
# ПРОТОКОЛ РОЗСИЛАННЯ КЛЮЧІВ
# ============================================================================

def SendKey(k: int, sender_private_key: Tuple[int, int, int], 
            receiver_public_key: Tuple[int, int]) -> Tuple[int, int]:
    """
    Відправник формує повідомлення (k1, S1) для передачі ключа
    k - ключ для передачі
    """
    d, p, q = sender_private_key
    n = p * q
    n1, e1 = receiver_public_key
    
    if n1 <= n:
        raise ValueError("n1 має бути більше за n")
    
    # Шифруємо ключ відкритим ключем отримувача
    k1 = power_mod(k, e1, n1)
    
    # Створюємо підпис
    S = power_mod(k, d, n)
    
    # Шифруємо підпис відкритим ключем отримувача
    S1 = power_mod(S, e1, n1)
    
    return k1, S1

def ReceiveKey(k1: int, S1: int, receiver_private_key: Tuple[int, int, int],
               sender_public_key: Tuple[int, int]) -> Optional[int]:
    """
    Отримувач розшифровує та перевіряє ключ
    Повертає ключ k якщо підпис вірний, інакше None
    """
    d1, p1, q1 = receiver_private_key
    n1 = p1 * q1
    n, e = sender_public_key
    
    # Розшифровуємо ключ
    k = power_mod(k1, d1, n1)
    
    # Розшифровуємо підпис
    S = power_mod(S1, d1, n1)
    
    # Перевіряємо підпис
    k_verified = power_mod(S, e, n)
    
    if k_verified == k:
        return k
    else:
        return None

# ============================================================================
# ТЕСТУВАННЯ ТА ДЕМОНСТРАЦІЯ
# ============================================================================

def main():
    print("=" * 70)
    print("ЛАБОРАТОРНА РОБОТА: КРИПТОСИСТЕМА RSA")
    print("=" * 70)
    
    # 1. Генерація простих чисел
    print("\n1. ГЕНЕРАЦІЯ ПРОСТИХ ЧИСЕЛ (256 біт)")
    print("-" * 70)
    
    p, q = generate_prime_pair(256)
    p1, q1 = generate_prime_pair(256)
    
    # Забезпечуємо умову p*q < p1*q1
    if p * q >= p1 * q1:
        p, q, p1, q1 = p1, q1, p, q
    
    print(f"Абонент A:")
    print(f"  p  = {p}")
    print(f"  q  = {q}")
    print(f"\nАбонент B:")
    print(f"  p1 = {p1}")
    print(f"  q1 = {q1}")
    
    # 2. Генерація ключів
    print("\n2. ГЕНЕРАЦІЯ КЛЮЧОВИХ ПАР")
    print("-" * 70)
    
    # Генеруємо ключі вручну з уже обраними p, q
    n_a = p * q
    phi_a = (p - 1) * (q - 1)
    e_a = 65537
    d_a = mod_inverse(e_a, phi_a)
    
    n_b = p1 * q1
    phi_b = (p1 - 1) * (q1 - 1)
    e_b = 65537
    d_b = mod_inverse(e_b, phi_b)
    
    public_key_A = (n_a, e_a)
    private_key_A = (d_a, p, q)
    
    public_key_B = (n_b, e_b)
    private_key_B = (d_b, p1, q1)
    
    print(f"Абонент A:")
    print(f"  Відкритий ключ:  n = {n_a}")
    print(f"                   e = {e_a}")
    print(f"  Секретний ключ:  d = {d_a}")
    
    print(f"\nАбонент B:")
    print(f"  Відкритий ключ:  n = {n_b}")
    print(f"                   e = {e_b}")
    print(f"  Секретний ключ:  d = {d_b}")
    
    # 3. Шифрування та розшифрування
    print("\n3. ШИФРУВАННЯ ТА РОЗШИФРУВАННЯ")
    print("-" * 70)
    
    # Генеруємо випадкове повідомлення
    M = random.randint(1, min(n_a, n_b) - 1)
    print(f"Відкрите повідомлення M = {M}")
    
    # A шифрує для B
    C_A_to_B = Encrypt(M, public_key_B)
    print(f"\nA шифрує для B:")
    print(f"  Криптограма C = {C_A_to_B}")
    
    M_decrypted = Decrypt(C_A_to_B, private_key_B)
    print(f"  B розшифровує: M' = {M_decrypted}")
    print(f"  Перевірка: M == M' -> {M == M_decrypted}")
    
    # 4. Цифровий підпис
    print("\n4. ЦИФРОВИЙ ПІДПИС")
    print("-" * 70)
    
    # A підписує повідомлення
    S_A = Sign(M, private_key_A)
    print(f"A підписує повідомлення M = {M}")
    print(f"  Підпис S = {S_A}")
    
    # Перевірка підпису
    is_valid = Verify(M, S_A, public_key_A)
    print(f"  Перевірка підпису: {is_valid}")
    
    # Перевірка з підробленим повідомленням
    M_fake = M + 1
    is_valid_fake = Verify(M_fake, S_A, public_key_A)
    print(f"  Перевірка з M' = {M_fake}: {is_valid_fake}")
    
    # 5. Протокол розсилання ключів
    print("\n5. ПРОТОКОЛ КОНФІДЕНЦІЙНОГО РОЗСИЛАННЯ КЛЮЧІВ")
    print("-" * 70)
    
    # A передає ключ k абоненту B
    k = random.randint(1, n_a - 1)
    print(f"A передає ключ k = {k} абоненту B")
    
    k1, S1 = SendKey(k, private_key_A, public_key_B)
    print(f"\nA формує повідомлення:")
    print(f"  k1 = {k1}")
    print(f"  S1 = {S1}")
    
    k_received = ReceiveKey(k1, S1, private_key_B, public_key_A)
    print(f"\nB отримує та перевіряє:")
    print(f"  k' = {k_received}")
    print(f"  Перевірка: k == k' -> {k == k_received}")
    
    print("\n" + "=" * 70)
    print("ВИКОНАННЯ ЗАВЕРШЕНО")
    print("=" * 70)

if __name__ == "__main__":
    main()