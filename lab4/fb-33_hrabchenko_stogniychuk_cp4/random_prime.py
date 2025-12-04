from mod import gcd, Horner
import random

BASE_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97
]

def trial_division(n):
    if n < 2:
        return False

    for p in BASE_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    return True

def miller_rabin(n, rounds):
    if n < 2:
        return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d >>= 1
        s += 1

    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        if gcd(a, n) > 1:
            return False

        x = Horner(a, d, n)
        if x == 1 or x == n - 1:
            continue

        composite = True
        for _ in range(s - 1):
            x = Horner(x, 2, n)
            if x == n - 1:
                composite = False
                break

        if composite:
            return False
    return True

def generate_prime(low, high, accuracy=10):
    """Генерує випадкове просте число і повертає список відхилених кандидатів."""
    rejected = []

    while True:
        candidate = random.randint(low, high)

        if not trial_division(candidate):
            rejected.append((candidate, "trial_division"))
            continue
        if not miller_rabin(candidate, accuracy):
            rejected.append((candidate, "miller_rabin"))
            continue

        return candidate, rejected

def generate_prime_pairs(bits):
    left = 2 ** (bits - 1)
    right = 2 ** bits - 1

    p, rejected_p = generate_prime(left, right)
    q, rejected_q = generate_prime(left, right)

    while True:
        p1, rejected_p1 = generate_prime(left, right)
        q1, rejected_q1 = generate_prime(left, right)

        if p * q <= p1 * q1:
            # повертаємо пари та всі відхилені кандидати
            return (p, q, rejected_p, rejected_q), (p1, q1, rejected_p1, rejected_q1)

if __name__ == "__main__":

    bit_len = 256  

    (p, q, rejected_p, rejected_q), (p1, q1, rejected_p1, rejected_q1) = generate_prime_pairs(bit_len)

    print("=" * 160)
    print(f"Перша пара простих:\n p  = {p}\n q  = {q}")
    print("Відхилені кандидати для p:")
    for num, reason in rejected_p:
        print(f"  * {num} — {reason}")
    print("Відхилені кандидати для q:")
    for num, reason in rejected_q:
        print(f"  * {num} — {reason}")

    print("-" * 160)
    print(f"Друга пара простих:\n p1 = {p1}\n q1 = {q1}")
    print("Відхилені кандидати для p1:")
    for num, reason in rejected_p1:
        print(f"  * {num} — {reason}")
    print("Відхилені кандидати для q1:")
    for num, reason in rejected_q1:
        print(f"  * {num} — {reason}")

    print("=" * 160)
    n1 = p * q
    n2 = p1 * q1
    print(f"n1 = p*q  = {n1}")
    print(f"n2 = p1*q1 = {n2}")

    if n1 <= n2:
        print("✔ Перевірка підтверджена: n1 <= n2")
    else:
        print("✘ Помилка: n1 > n2")
