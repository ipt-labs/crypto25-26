import random

from modular_arithemtic import mod_pow_horner, gcd

def trial_division(n: int) -> bool:
    if n < 2:
        return False

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    return True

def miller_rabin_test(p: int, k: int=7) -> bool:
    if not trial_division(p):
        return False

    d = p - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    count = 0

    while count < k:
        x = random.randrange(2, p)

        if gcd(x, p) != 1:
            return False
        a = mod_pow_horner(x, d, p)
        if a == 1 or a == p - 1:
            count += 1
            continue

        for r in range(1, s):
            a = mod_pow_horner(a, 2, p)
            if a == p - 1:
                break
        else:
            return False

        count += 1
    return True

def generate_strong_prime(*, bits: int=None, start: int=None, end: int=None) -> int:
    if bits is not None:
        if start is not None or end is not None:
            print(f"Start and end would be ignored as certain number of bits was mentioned")
        start = 2 ** (bits - 1)
        end = 2 ** (bits + 50)
    elif start is None or end is None:
        raise ValueError("Start and end must be provided if number of bits was not mentioned")

    while True:
        candidate = random.randrange(start, end)
        if miller_rabin_test(candidate):
            i = 0
            while True:
                i += 1
                p = 2 * i * candidate + 1
                if p.bit_length() > end.bit_length():
                    break
                if miller_rabin_test(p):
                    return p