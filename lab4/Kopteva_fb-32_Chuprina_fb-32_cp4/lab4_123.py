import random
import math
from typing import Tuple


BIT_LENGTH = 256
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]


class KeyPair:
    def __init__(self, p: int, q: int, d: int, e: int, n: int):
        self.p = p
        self.q = q
        self.d = d
        self.e = e
        self.n = n


def mod_pow(base: int, exp: int, mod: int) -> int:
    res = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % mod
        base = (base * base) % mod
        exp //= 2
    return res


def gcd_extended(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = gcd_extended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def mod_inverse(a: int, m: int) -> int:
    gcd, x, y = gcd_extended(a, m)
    if gcd != 1:
        raise ValueError("Модульне обернене число не існує.")
    return x % m


def miller_rabin(n: int, k: int = 40) -> bool:
    if n <= 3:
        return n > 1
    if n % 2 == 0:
        return False

    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = mod_pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        is_composite = True
        for _ in range(s - 1):
            x = mod_pow(x, 2, n)
            if x == n - 1:
                is_composite = False
                break

        if is_composite:
            return False
    return True


def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    return miller_rabin(n, k=40)


def get_random_prime(bits: int) -> int:
    min_val = 1 << (bits - 1)

    candidate = random.getrandbits(bits)
    candidate |= 1
    candidate |= min_val

    while True:
        if is_prime(candidate):
            return candidate
        candidate += 2


def GenerateKeyPair(p: int, q: int) -> KeyPair:
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537
    while math.gcd(e, phi_n) != 1:
        e += 2

    d = mod_inverse(e, phi_n)

    return KeyPair(p, q, d, e, n)


def generate_and_check_primes() -> Tuple[KeyPair, KeyPair]:
    print(
        f"\n--- ЗАВДАННЯ 1, 2, 3: ГЕНЕРАЦІЯ КЛЮЧІВ RSA (Min {BIT_LENGTH} bits) ---")
    p_A = get_random_prime(BIT_LENGTH)
    q_A = get_random_prime(BIT_LENGTH)
    n_A = p_A * q_A

    while True:
        p_B = get_random_prime(BIT_LENGTH)
        q_B = get_random_prime(BIT_LENGTH)
        n_B = p_B * q_B

        if n_A <= n_B:
            break

    print(
        f"Статус: N_A ({n_A.bit_length()} bits) <= N_B ({n_B.bit_length()} bits) - OK")

    keys_A = GenerateKeyPair(p_A, q_A)
    keys_B = GenerateKeyPair(p_B, q_B)

    print("\n--- ПОВНІ КЛЮЧІ АБОНЕНТА A ---")
    print(f"N (Модуль): {keys_A.n}")
    print(f"N довжина: {keys_A.n.bit_length()} біт")
    print(f"  p ({keys_A.p.bit_length()} bits): {keys_A.p}")
    print(f"  q ({keys_A.q.bit_length()} bits): {keys_A.q}")
    print(f"Відкритий ключ (e, N): e = {keys_A.e}")
    print(f"Секретний ключ (d, p, q): d = {keys_A.d}")

    print("\n--- ПОВНІ КЛЮЧІ АБОНЕНТА B ---")
    print(f"N1 (Модуль): {keys_B.n}")
    print(f"N1 довжина: {keys_B.n.bit_length()} біт")
    print(f"  p1 ({keys_B.p.bit_length()} bits): {keys_B.p}")
    print(f"  q1 ({keys_B.q.bit_length()} bits): {keys_B.q}")
    print(f"Відкритий ключ (e1, N1): e1 = {keys_B.e}")
    print(f"Секретний ключ (d1, p1, q1): d1 = {keys_B.d}")

    return keys_A, keys_B


if __name__ == '__main__':
    generate_and_check_primes()
