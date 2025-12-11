import random
import math
import hashlib
import sys
from typing import Tuple

print("""
--- ФОРМУЛИ RSA ---

1. Генерація простих чисел:
   - шукаємо p, q такими що:
       n = p · q
       p, q — прості
   - перевірка: тест Міллера-Рабіна

2. Функція Ейлера:
       φ(n) = (p − 1)(q − 1)

3. Вибір відкритого експонента:
       2 < e < φ(n)
       gcd(e, φ(n)) = 1

4. Секретний експонент:
       d ≡ e⁻¹ (mod φ(n))
       e·d ≡ 1 (mod φ(n))

5. Відкритий ключ:  (n, e)
   Приватний ключ: (d, p, q)

-----------------------------------------
""")

sys.setrecursionlimit(2000)
random.seed()
LOG_FILE = "prime_generation_log.txt"

_SMALL_PRIMES = [
    2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
    73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,
    157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,
    239,241,251,257,263,269,271,277,281,283,293
]

def log(text: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def _is_divisible_by_small_primes(n: int) -> bool:
    for p in _SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    return True

def _decompose(n: int) -> Tuple[int,int]:
    s = 0
    d = n
    while d % 2 == 0:
        d //= 2
        s += 1
    return s, d

def is_probable_prime(n: int, k: int = 20) -> bool:
    if n < 2:
        log(f"Число {n} не пройшло тест Міллера-Рабіна (n < 2)")
        return False
    for p in _SMALL_PRIMES:
        if n == p:
            log(f"Число {n} є малим простим")
            return True
        if n % p == 0:
            log(f"Число {n} ділиться на мале просте {p}, не просте")
            return False
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
            log(f"Число {n} не пройшло тест Міллера-Рабіна")
            print(f"Число {n} не пройшло тест Міллера-Рабіна")
            return False
    log(f"Число {n} є ймовірно простим (пройшло Міллер-Рабін)")
    print(f"Число {n} є ймовірно простим (пройшло Міллер-Рабін)")
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
    return pow(c, d, p*q)

def decrypt_from_n(c, d, n):
    return pow(c, d, n)

def int_from_sha256(data: bytes) -> int:
    return int.from_bytes(hashlib.sha256(data).digest(), 'big')

def sign(msg_bytes, priv):
    d, p, q = priv
    h = int_from_sha256(msg_bytes) % (p*q)
    return pow(h, d, p*q)

def verify(msg_bytes, sig, pub):
    e, n = pub
    h = int_from_sha256(msg_bytes) % n
    return pow(sig, e, n) == h

def send_key(sender_priv, receiver_pub):
    e_r, n_r = receiver_pub
    k = random.randrange(1, n_r)
    c = pow(k, e_r, n_r) 
    k_bytes = k.to_bytes((k.bit_length()+7)//8, 'big')
    sig = sign(k_bytes, sender_priv)
    sig_encrypted = pow(sig, e_r, n_r)
    return c, sig_encrypted

def receive_key(receiver_priv, sender_pub, c, sig_encrypted):
    d, p, q = receiver_priv
    n = sender_pub[1]
    k = pow(c, d, p*q)
    sig = pow(sig_encrypted, d, p*q)
    k_bytes = k.to_bytes((k.bit_length()+7)//8, 'big')
    valid = verify(k_bytes, sig, sender_pub)
    return k, valid

def _test_all():
    print("=== Генерація ключів A і B ===")
    while True:
        pubA, privA = generate_keypair()
        pubB, privB = generate_keypair()
        if pubA[1] <= pubB[1]:
            break
    eA, nA = pubA
    dA, pA, qA = privA
    eB, nB = pubB
    dB, pB, qB = privB
    print("\n=== Ключі абонента A ===")
    print(f"pA = {pA}")
    print(f"qA = {qA}")
    print(f"nA = {nA}")
    print(f"eA = {eA}")
    print(f"dA = {dA}")
    print("\n=== Ключі абонента B ===")
    print(f"pB = {pB}")
    print(f"qB = {qB}")
    print(f"nB = {nB}")
    print(f"eB = {eB}")
    print(f"dB = {dB}")
    print("\nКлючі збережено у файли.")
    print("\n=== Тест шифрування ===")
    M = random.randrange(2, min(nA, nB)-1)
    C = encrypt(M, pubA)
    M2 = decrypt(C, privA)
    print(f"M = {M}")
    print(f"C = {C}")
    print(f"Розшифровано: {M2}")
    print("\n=== Тест цифрового підпису ===")
    msg = b"Hello RSA"
    sig = sign(msg, privA)
    print("Підпис валідний?", verify(msg, sig, pubA))
    print("\n=== Протокол передачі ключа A → B ===")
    c, sig2 = send_key(privA, pubB)
    k, ok = receive_key(privB, pubA, c, sig2)
    print(f"Отримано ключ k = {k}, Підпис валідний? {ok}")
    
def hex_to_int(s: str) -> int:
    """Перетворює hex-рядок у int"""
    return int(s.replace(" ", "").replace("\n", ""), 16)

def test_external_data():
    print("\n=== Тест даних із сайту ===")
    
    modulus_hex = "91B5E8342B2E35A9B66CD3E7AF68E61A78CB18F0E68B79D0DB11A8361D0EA091"
    pubexp_hex = "10001"
    ciphertext_hex = "24D92CA039EAFA65A946734D82613CCE3887297D94F92497CEE85209C2CDA11A"
    signature_hex = "580C9D78B7151488304E2867EB2D4151B03277480C4D3E4B461C88154CB0D262"
    message = b"Kitty"

    n = hex_to_int(modulus_hex)
    e = hex_to_int(pubexp_hex)
    c = hex_to_int(ciphertext_hex)
    sig = hex_to_int(signature_hex)

    pub = (e, n)
    
    valid = verify(message, sig, pub)
    print(f"Перевірка підпису: {valid}")

if __name__ == "__main__":
    _test_all()
    test_external_data()


