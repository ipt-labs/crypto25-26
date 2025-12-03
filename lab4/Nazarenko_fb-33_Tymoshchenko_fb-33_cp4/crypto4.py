import random
#  мат функції 
def gcd(a, b):
    # Алгоритм Евкліда для знаходження НСД(a, b)
    while b:
        a, b = b, a % b
    return a

def extended_euclid(a, b):
    # Розширений алгоритм Евкліда: знаходить x, y такі що ax + by = gcd(a, b)
    if b == 0:
        return a, 1, 0
    d, x1, y1 = extended_euclid(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return d, x, y

def modexp(base, exp, mod):
    # Швидке піднесення до степеня за модулем 
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result

#  тест на простоту
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
                79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163,
                167, 173, 179, 181, 191, 193, 197, 199]

def trial_division(n):
    # Перевірка діленням на малі прості числа
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    return True

def is_prime(n, k=10):
    # Імовірнісний тест простоти Міллера–Рабіна зі стартовими пробними діленнями
    if n < 2 or n % 2 == 0:
        return False
    if not trial_division(n):
        return False
    # Подання n − 1 у вигляді d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d >>= 1
        s += 1
    # k незалежних раундів тесту
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = modexp(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(s - 1):
            x = modexp(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True



def generate_prime(bits=256):
    # Генерація випадкового простого числа з інтервалу [2^(bits-1), 2^bits − 1]
    lower = 1 << (bits - 1)
    upper = (1 << bits) - 1
    failed = []

    while True:
        n = random.randint(lower, upper)
        if is_prime(n):
            if failed:
                print(f"Кандидати, що не пройшли: {len(failed)}")
            return n
        failed.append(n)


def GenerateKeyPair(bits=256):
    p = generate_prime(bits)
    q = generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    # Вибір випадкового відкритого експонента e (умова gcd(e, ф(n)) = 1)
    e = random.randint(2, phi - 1)
    while gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)
    # Знаходження секретної експоненти d
    _, d, _ = extended_euclid(e, phi)
    d %= phi
    public_key = (n, e)
    private_key = (d, p, q)
    return public_key, private_key

def Encrypt(M, public_key):
    n, e = public_key
    return modexp(M, e, n)

def Decrypt(C, private_key):
    d, p, q = private_key
    n = p * q
    return modexp(C, d, n)

#  Цифровий підпис

def Sign(M, private_key):
    d, p, q = private_key
    n = p * q
    return modexp(M, d, n)


def Verify(M, S, public_key):
    n, e = public_key
    return M == modexp(S, e, n)

#  Розсилка ключів

def SendKey(k, private_key_A, public_key_B):
    # A створює підпис S і шифрує k -> k1
    dA, pA, qA = private_key_A
    nA = pA * qA

    S = modexp(k, dA, nA)     # цифровий підпис
    nB, eB = public_key_B
    k1 = modexp(k, eB, nB)    # зашифрований ключ

    return k1, S


def ReceiveKey(k1, S, private_key_B, public_key_A):
    # B розшифровує k1 та перевіряє підпис S
    dB, pB, qB = private_key_B
    nB = pB * qB

    k = modexp(k1, dB, nB)

    nA, eA = public_key_A
    valid = (k == modexp(S, eA, nA))

    return k, valid

#  Запуск

def demo():

    print("===============================")
    print("   ГЕНЕРАЦІЯ КЛЮЧІВ А")
    print("===============================")
    pubA, privA = GenerateKeyPair()
    nA, eA = pubA
    dA, pA, qA = privA

    print("\nВідкритий ключ A:")
    print(f"n = {nA}")
    print(f"e = {eA}")

    print("\nСекретний ключ A:")
    print(f"p = {pA}")
    print(f"q = {qA}")
    print(f"d = {dA}")

    print("\n===============================")
    print("   ГЕНЕРАЦІЯ КЛЮЧІВ B")
    print("===============================")
    pubB, privB = GenerateKeyPair()
    nB, eB = pubB
    dB, pB, qB = privB

    print("\nВідкритий ключ B:")
    print(f"n = {nB}")
    print(f"e = {eB}")

    print("\nСекретний ключ B:")
    print(f"p1 = {pB}")
    print(f"q1 = {qB}")
    print(f"d1 = {dB}")

    # Забезпечення умови pq ≤ p1q1
    if nA > nB:
        pubA, pubB = pubB, pubA
        privA, privB = privB, privA
        nA, nB = nB, nA
        eA, eB = eB, eA

    print("\n===============================")
    print("   ШИФРУВАННЯ / РОЗШИФРУВАННЯ")
    print("===============================")

    M = random.randint(2, nA - 1)
    C = Encrypt(M, pubA)
    M2 = Decrypt(C, privA)

    print("\nВихідне повідомлення (M):")
    print(M)

    print("\nЗашифроване повідомлення (C):")
    print(C)

    print("\nРозшифрування:")
    print(M2, "(вірно)" if M2 == M else "(помилка)")

    print("===============================")
    print("ЦИФРОВИЙ ПІДПИС")
    print("===============================")
    print("\n[1] Повідомлення, яке підписуємо:")
    print("M =", M)

    # Підписування
    S = Sign(M, privA)
    print("\n[2] Формування підпису:")
    print("S = M^d_A mod n_A =")
    print(S)

    # Перевірка
    print("\n[3] Перевірка підпису:")
    check = modexp(S, eA, nA)
    print("S^e_A mod n_A =", check)
    print("Очікується     =", M)

    print("\nРезультат:")
    print("Успіх - підпис підтверджено" if check == M else "Помилка")

    print("\n===============================")
    print(" ПРОТОКОЛ РОЗСИЛАННЯ СЕКРЕТНОГО КЛЮЧА")
    print("===============================")

    # 1. A генерує секретний ключ k
    k = random.randint(2, nA - 1)
    print("\n[1] Початковий секретний ключ k:")
    print(k)

    # 2. A формує k1 та S
    k1, S1 = SendKey(k, privA, pubB)

    print("\n[2] Підпис S = k^d_A mod n_A:")
    print(S1)

    print("\n[3] A шифрує k відкритим ключем B -> k1:")
    print(k1)

    print("\n[4] A -> B надсилає (k1, S):")
    print("k1 =", k1)
    print("S  =", S1)

    # 3. B приймає та перевіряє
    k2, valid = ReceiveKey(k1, S1, privB, pubA)

    print("\n[5] B розшифровує k1 своїм секретним ключем:")
    print("k2 =", k2)

    print("\n[6] Детальна перевірка підпису:")
    SA_check = modexp(S1, eA, nA)
    print("S^e_A mod n_A =", SA_check) 
    print("Очікуване значення =", k2)

    print("\nРезультат перевірки:")
    print("Успіх - підпис підтверджено" if valid else "Помилка - підпис недійсний")


if __name__ == "__main__":
    demo()
