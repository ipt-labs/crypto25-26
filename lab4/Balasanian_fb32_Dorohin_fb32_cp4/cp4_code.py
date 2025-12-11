import secrets
import math

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

_SMALL_PRIMES = [
     2,  3,  5,  7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113
]


def _trial_division(n: int) -> bool:
    if n < 2:
        return False
    for p in _small_primes_to_check(n):
        if n == p:
            return True
        if n % p == 0:
            return False
    return True


def _small_primes_to_check(n: int):
    for p in _SMALL_PRIMES:
        if p * p > n:
            break
        yield p


def miller_rabin(n: int, rounds: int = 10) -> bool:
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
        
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2 
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        skip_to_next_n = False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                skip_to_next_n = True
                break
            if x == 1:
                return False
        if not skip_to_next_n:
            return False
    return True


def random_prime(bits: int) -> int:
    if bits < 2:
        raise ValueError("Кількість бітів має бути не менше 2")

    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if _trial_division(candidate) and miller_rabin(candidate):
            return candidate

def generate_rsa_keypair(bits: int = 256):
    p = random_prime(bits)
    q = random_prime(bits)
    while q == p:
        q = random_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if math.gcd(e, phi) != 1:
        while True:
            e = secrets.randbelow(phi - 2) + 2
            if math.gcd(e, phi) == 1:
                break

    d = mod_inverse(e, phi)
    if d is None:
        raise RuntimeError("Не вдалося знайти обернений елемент для e")

    public_key = (n, e)
    private_key = (d, p, q)
    return public_key, private_key

def rsa_encrypt(m: int, public_key):
    n, e = public_key
    if not (0 <= m < n):
        raise ValueError("Повідомлення має бути в діапазоні [0, n)")
    return pow(m, e, n)


def rsa_decrypt(c: int, private_key, public_key):
    n, _ = public_key
    d, p, q = private_key
    return pow(c, d, n)


def rsa_sign(m: int, private_key, public_key):
    n, _ = public_key
    d, _, _ = private_key
    return pow(m, d, n)


def rsa_verify(m: int, signature: int, public_key) -> bool:
    n, e = public_key
    return m % n == pow(signature, e, n)

class Participant:
    def __init__(self, name: str, bits: int = 256):
        self.name = name
        self.public_key, self.private_key = generate_rsa_keypair(bits)

    def encrypt_for(self, other_public, m: int) -> int:
        return rsa_encrypt(m, other_public)

    def decrypt(self, c: int) -> int:
        return rsa_decrypt(c, self.private_key, self.public_key)

    def sign(self, m: int) -> int:
        return rsa_sign(m, self.private_key, self.public_key)

    def verify_from(self, other_public, m: int, s: int) -> bool:
        return rsa_verify(m, s, other_public)


def send_session_key(sender: Participant, receiver: Participant, k: int):
    n_B, _ = receiver.public_key
    if not (0 < k < n_B):
        raise ValueError("k має задовольняти 0 < k < n_B")

    s = sender.sign(k)
    c_k = sender.encrypt_for(receiver.public_key, k)
    c_s = sender.encrypt_for(receiver.public_key, s)
    return c_k, c_s

    # Тест шифрування/розшифрування і підпису для A
    M_A = secrets.randbelow(n_A - 1) + 1
    C_A = rsa_encrypt(M_A, A.public_key)
    M_A_dec = rsa_decrypt(C_A, A.private_key, A.public_key)
    S_A = rsa_sign(M_A, A.private_key, A.public_key)
    ok_A = rsa_verify(M_A, S_A, A.public_key)

    # Аналогічно для B
    M_B = secrets.randbelow(n_B - 1) + 1
    C_B = rsa_encrypt(M_B, B.public_key)
    M_B_dec = rsa_decrypt(C_B, B.private_key, B.public_key)
    S_B = rsa_sign(M_B, B.private_key, B.public_key)
    ok_B = rsa_verify(M_B, S_B, B.public_key)

def receive_session_key(receiver: Participant, sender: Participant, c_k: int, c_s: int):
    k = receiver.decrypt(c_k)
    s = receiver.decrypt(c_s)
    ok = receiver.verify_from(sender.public_key, k, s)
    return k, ok

def main():
    print("=== Генерація ключів RSA для абонентів A та B ===\n")

    A = Participant("A", bits=256)
    B = Participant("B", bits=256)

    n_A, e_A = A.public_key
    n_B, e_B = B.public_key
    d_A, p_A, q_A = A.private_key
    d_B, p_B, q_B = B.private_key

    # Забезпечуємо умову n_A ≥ 2·n_B (як в методичці для протоколу)
    while n_A < n_B:
        print("n_A < 2 * n_B, перегенеруємо ключі A...")
        A = Participant("A", bits=256)
        n_A, e_A = A.public_key
        d_A, p_A, q_A = A.private_key

    print("Публічний ключ A: (n_A, e_A)")
    print("n_A =", n_A)
    print("e_A =", e_A)
    print("Секретний ключ A: (d_A, p_A, q_A)")
    print("d_A =", d_A, "\n")

    print("Публічний ключ B: (n_B, e_B)")
    print("n_B =", n_B)
    print("e_B =", e_B)
    print("Секретний ключ B: (d_B, p_B, q_B)")
    print("d_B =", d_B, "\n")

    # === Перевірка шифрування/розшифрування і цифрового підпису для A ===
    M_A = secrets.randbelow(n_A - 1) + 1   # 0 < M_A < n_A
    C_A = rsa_encrypt(M_A, A.public_key)
    M_A_dec = rsa_decrypt(C_A, A.private_key, A.public_key)
    S_A = rsa_sign(M_A, A.private_key, A.public_key)
    ok_A = rsa_verify(M_A, S_A, A.public_key)

    print("=== Перевірка операцій для A ===")
    print("M_A      =", M_A)
    print("C_A      =", C_A)
    print("M_A'     =", M_A_dec)
    print("Підпис коректний для A:", ok_A, "\n")

    # === Перевірка шифрування/розшифрування і цифрового підпису для B ===
    M_B = secrets.randbelow(n_B - 1) + 1   # 0 < M_B < n_B
    C_B = rsa_encrypt(M_B, B.public_key)
    M_B_dec = rsa_decrypt(C_B, B.private_key, B.public_key)
    S_B = rsa_sign(M_B, B.private_key, B.public_key)
    ok_B = rsa_verify(M_B, S_B, B.public_key)

    print("=== Перевірка операцій для B ===")
    print("M_B      =", M_B)
    print("C_B      =", C_B)
    print("M_B'     =", M_B_dec)
    print("Підпис коректний для B:", ok_B, "\n")

    # Вибір сесійного ключа k: 0 < k < n_A (як у методичці)
    k = secrets.randbelow(n_B - 1) + 1

    print("=== Випадковий передаваний ключ k ===")
    print("k =", k, "\n")

    c_k, c_s = send_session_key(A, B, k)

    print("=== Дані, які формує відправник A ===")
    s = A.sign(k)
    print("Підпис s =", s)
    print("Зашифрований ключ C_k =", c_k)
    print("Зашифрований підпис C_s =", c_s, "\n")

    k_recv, ok = receive_session_key(B, A, c_k, c_s)

    print("=== Дані, які отримує одержувач B ===")
    print("Отриманий ключ k' =", k_recv)
    print("Підпис коректний:", ok)

    if ok and k_recv == k:
        print("\nПротокол виконано успішно.")
    else:
        print("\nСталася помилка в протоколі.")


if __name__ == "__main__":
    main()