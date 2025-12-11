import random
import math
import hashlib
import sys
from typing import Tuple

sys.setrecursionlimit(2000)
random.seed()

_SMALL_PRIMES = [
    2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
    73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,
    157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,
    239,241,251,257,263,269,271,277,281,283,293
]

def _decompose(n: int) -> Tuple[int,int]:
    s = 0
    d = n
    while d % 2 == 0:
        d //= 2
        s += 1
    return s, d

def is_probable_prime(n: int, k: int = 20) -> bool:
    if n < 2: return False
    for p in _SMALL_PRIMES:
        if n == p: return True
        if n % p == 0: return False
    s, d = _decompose(n - 1)
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True

def random_odd_with_bitlen(bits: int) -> int:
    n = random.getrandbits(bits)
    n |= (1 << (bits - 1))
    n |= 1
    return n

def random_prime(bits: int, tries_limit: int = 100000) -> int:
    for _ in range(tries_limit):
        candidate = random_odd_with_bitlen(bits)
        if is_probable_prime(candidate, k=40):
            return candidate
    raise RuntimeError("Не знайдено просте число")

def egcd(a: int, b: int):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("modular inverse does not exist")
    return x % m

def generate_keypair(bits_p=256, bits_q=256, e=65537):
    """
    Возвращает ((e, n), (d, p, q))
    """
    while True:
        p = random_prime(bits_p)
        q = random_prime(bits_q)
        if p == q:
            continue
        n = p * q
        phi = (p - 1) * (q - 1)
        if math.gcd(e, phi) == 1:
            d = modinv(e, phi)
            return (e, n), (d, p, q)

def encrypt(m, pub):
    e, n = pub
    return pow(m, e, n)

def decrypt(c, priv):
    d, p, q = priv
    # Расшифровка через d и n (n = p*q)
    return pow(c, d, p*q)

def int_from_sha256(data: bytes) -> int:
    return int.from_bytes(hashlib.sha256(data).digest(), 'big')

def sign(msg_bytes, priv):
    d, p, q = priv
    m = int.from_bytes(msg_bytes, 'big')
    
    if m >= (p * q):
        raise ValueError("Повідомлення занадто довге для цього ключа!")
        
    return pow(m, d, p*q)

def verify(msg_bytes, sig, pub):
    e, n = pub
    h = int_from_sha256(msg_bytes) % n
    return pow(sig, e, n) == h

def main():
    print("========================================")
    print("      RSA ЛАБОРАТОРНАЯ (INTERACTIVE)    ")
    print("========================================")
    
    print(">>> [0] Генеруємо пару ключів (чекайте)...")
    pub_key, priv_key = generate_keypair(256, 256) 
    
    e, n = pub_key

    print("\n----------------------------------------")
    print("   ДАНІ ДЛЯ ВСТАВКИ НА САЙТ (HEX)      ")
    print("----------------------------------------")

    print(f"Modulus (n): {hex(n)[2:].upper()}")
    print(f"Public Exponent (e): {hex(e)[2:].upper()}")
    
    print("\n----------------------------------------")
    print("   [1] ЗАВДАННЯ: РОЗШИФРУВАННЯ (Decrypt)")
    print("----------------------------------------")
    print("Скопіюйте 'Ciphertext' із сайту сюди.")
    
    c_hex = input("Ciphertext (HEX) >>> ").strip().replace(" ", "")
    
    if c_hex:
        try:
            c_int = int(c_hex, 16)
            decrypted_int = decrypt(c_int, priv_key)
            
            print(f"\n>> Розшифровано (int): {decrypted_int}")
            
            try:
                byte_len = (decrypted_int.bit_length() + 7) // 8
                decrypted_text = decrypted_int.to_bytes(byte_len, 'big').decode('utf-8')
                print(f">> Розшифровано (text): {decrypted_text}")
            except Exception:
                print(">> (Результат не схожий на текст, залишаємо як число)")
                
        except Exception as err:
            print(f"Помилка при розшифруванні: {err}")
    else:
        print("Пропущено.")

    print("\n----------------------------------------")
    print("   [2] ЗАВДАННЯ: ЦИФРОВИЙ ПІДПИС (Sign)")
    print("----------------------------------------")
    
    msg_str = "Hello World"
    print(f"Повідомлення за замовчуванням: '{msg_str}'")
    user_msg = input("Введіть своє повідомлення (або Enter для 'Hello World'): ")
    if user_msg:
        msg_str = user_msg

    msg_bytes = msg_str.encode('utf-8')
    sig_int = sign(msg_bytes, priv_key)

    print(f"\nMessage: {msg_str}")
    print(f"Signature (HEX): {hex(sig_int)[2:].upper()}")
    print(f"(Вставте цей Signature та Modulus/Exponent на сайті для перевірки)")

if __name__ == "__main__":
    main()