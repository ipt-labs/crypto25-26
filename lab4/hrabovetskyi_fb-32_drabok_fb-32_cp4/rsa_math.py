import random

def extended_gcd(a, b):
    """Розширений алгоритм Евкліда."""
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = extended_gcd(b % a, a)
        return gcd, y - (b // a) * x, x


def mod_inverse(a, m):
    """Знаходження оберненого елемента за модулем."""
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % m


def miller_rabin_test(p, k=40):
    """
    Імовірнісний тест Міллера-Рабіна.
    Перевіряє, чи є число p псевдопростим.
    """
    if p == 2 or p == 3: return True
    if p % 2 == 0 or p < 2: return False

    s = 0
    d = p - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        x = random.randrange(2, p - 1)

        x_r = pow(x, d, p)
        if x_r == 1 or x_r == p - 1:
            continue

        for _ in range(s - 1):
            x_r = pow(x_r, 2, p)
            if x_r == p - 1:
                break
        else:
            return False

    return True


def generate_prime(bits):
    """
    Генерація великого простого числа.
    Використовує тест пробних ділень та тест Міллера-Рабіна.
    """
    while True:
        candidate = random.getrandbits(bits)
        if candidate % 2 == 0:
            candidate += 1

        small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29]
        if any(candidate % sp == 0 for sp in small_primes):
            continue

        if miller_rabin_test(candidate):
            return candidate