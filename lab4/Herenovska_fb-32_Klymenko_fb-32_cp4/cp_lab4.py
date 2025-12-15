import random
import sys

sys.setrecursionlimit(5000)

def power(a, b, m):
    res = 1
    a %= m
    while b > 0:
        if b % 2 == 1:
            res = (res * a) % m
        a = (a * a) % m
        b //= 2
    return res

def gcd_extended(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = gcd_extended(b % a, a)
        return g, x - (b // a) * y, y

def mod_inverse(a, m):
    g, x, y = gcd_extended(a, m)
    if g != 1:
        raise Exception('Обернений елемент за модулем не існує')
    else:
        return (x % m + m) % m

def miller_rabin_test(n, k=40):
    if n == 2 or n == 3: return True
    if n % 2 == 0 or n < 2: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = power(a, d, n)
        if x == 1 or x == n - 1:
            continue
        is_composite = True
        for _ in range(r - 1):
            x = power(x, 2, n)
            if x == n - 1:
                is_composite = False
                break
        if is_composite:
            return False
    return True

def generate_prime(bits, log_failures=True):
    while True:
        candidate = random.getrandbits(bits)
        if candidate % 2 == 0:
            candidate += 1
        mask = (1 << (bits - 1)) | 1
        candidate |= mask
        if candidate % 3 == 0 or candidate % 5 == 0 or candidate % 7 == 0:
            if log_failures:
                print(f"Кандидат {candidate} відсіяний перевіркою пробним діленням")
            continue
        if miller_rabin_test(candidate):
            print(f"Знайдено просте число: {candidate}")
            return candidate
        else:
            if log_failures:
                print(f"Кандидат {candidate} відсіяний тестом Міллера-Рабіна")

def GenerateKeyPair(bits=256):
    print(f"\nГенерація ключової пари RSA довжиною ({bits} біт)")
    p = generate_prime(bits)
    q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    while gcd_extended(e, phi)[0] != 1:
        e += 2
    d = mod_inverse(e, phi)
    return (e, n), (d, n), p, q

def Encrypt(message_int, public_key):
    e, n = public_key
    if message_int >= n:
        raise ValueError("Повідомлення завелике(більше за модуль n)")
    return power(message_int, e, n)

def Decrypt(ciphertext_int, private_key):
    d, n = private_key
    return power(ciphertext_int, d, n)

def Sign(message_int, private_key):
    d, n = private_key
    return power(message_int, d, n)

def Verify(message_int, signature, public_key):
    e, n = public_key
    return power(signature, e, n) == message_int

def SendKey(k, key_pair_A, public_key_B):
    print("\nПротокол конфіденційного розсилання ключів (Абонент А):")
    d_A, n_A = key_pair_A[0]
    e_B, n_B = public_key_B
    S = Sign(k, (d_A, n_A))
    print(f"1. Підпис сформовано (S):{S}")
    k1 = Encrypt(k, (e_B, n_B))
    S1 = Encrypt(S, (e_B, n_B))
    print(f"2. k зашифровано (k1): {k1}")
    print(f"3. S зашифровано (S1): {S1}")
    return k1, S1

def ReceiveKey(package, key_pair_B, public_key_A):
    print("\nПротокол конфіденційного розсилання ключів (Абонент В):")
    k1, S1 = package
    d_B, n_B = key_pair_B[0]
    e_A, n_A = public_key_A
    k_prime = Decrypt(k1, (d_B, n_B))
    S_prime = Decrypt(S1, (d_B, n_B))
    print(f"Розшифровано k': {k_prime}")
    print(f"Розшифровано S': {S_prime}")
    if Verify(k_prime, S_prime, (e_A, n_A)):
        print("Підпис валідний. Автентифікація пройдена")
        return k_prime
    else:
        print("Підпис невірний")
        return None

if __name__ == "__main__":
    
    print("\nГенерація параметрів криптосистеми для Абонента А")
    pub_A, priv_A, p_A, q_A = GenerateKeyPair(256)
    print(f"Відкритий ключ A (e, n): {pub_A}\nСекретний ключ A (d, n): {priv_A}")
    print(f"A p: {p_A}\nA q: {q_A}")

    print("\nГенерація параметрів криптосистеми для Абонента В")
    while True:
        pub_B, priv_B, p_B, q_B = GenerateKeyPair(256)
        if pub_B[1] >= pub_A[1]:
            print(f"Умова n_B >= n_A виконана.")
            break
        else:
            print(f"n_B < n_A. Повторна генерація параметрів для B...")
            
    print(f"Відкритий ключ B (e, n): {pub_B}\nСекретний ключ B (d, n): {priv_B}")
    print(f"B p: {p_B}\nB q: {q_B}")

    print("\n Тест RSA (Шифрування)")
    msg = 123456789012345
    print(f"Відкрите повідомлення M: {msg}")
    encrypted = Encrypt(msg, pub_B)
    print(f"Шифртекст (криптограма) С: {encrypted}")
    decrypted = Decrypt(encrypted, priv_B)
    print(f"Розшифровано: {decrypted}")
    
    print("\n Тест Цифрового Підпису")
    msg_sign = 987654321
    print(f"Повідомлення для підпису M: {msg_sign}")
    signature = Sign(msg_sign, priv_A)
    print(f"Цифровий підпис S: {signature}")
    valid = Verify(msg_sign, signature, pub_A)
    print(f"Результат перевірки підпису:{valid}")

    print("\nЗапуск протоколу конфіденційного розсилання ключів")
    k_session = random.randint(1, pub_A[1] // 2)
    print(f"Секретний ключ k: {k_session}")
    package = SendKey(k_session, (priv_A, pub_A), pub_B)
    received_k = ReceiveKey(package, (priv_B, pub_B), pub_A)
    
    if k_session == received_k:
        print(f"\nПротокол завершено. Ключі співпадають")
    else:
        print(f"\nПомилка виконання протоколу")