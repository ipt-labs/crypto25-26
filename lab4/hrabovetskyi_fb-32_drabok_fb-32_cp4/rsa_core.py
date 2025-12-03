import random
from rsa_math import generate_prime, extended_gcd, mod_inverse


def GenerateKeyPair(bits=256):
    """
    Генерація ключових пар для RSA.
    Повертає: ((d, p, q), (n, e))
    """
    p = generate_prime(bits)
    q = generate_prime(bits)
    while p == q:
        q = generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    while extended_gcd(e, phi)[0] != 1:
        e = random.randrange(3, phi, 2)

    d = mod_inverse(e, phi)

    return ((d, p, q), (n, e))


def Encrypt(message, public_key):
    """Шифрування: C = M^e mod n"""
    n, e = public_key
    if message >= n:
        raise ValueError("Message is too large for the modulus n")
    return pow(message, e, n)


def Decrypt(ciphertext, private_key_full):
    """Розшифрування: M = C^d mod n"""
    d, p, q = private_key_full
    n = p * q
    return pow(ciphertext, d, n)


def Sign(message, private_key_full):
    """Цифровий підпис: S = M^d mod n"""
    d, p, q = private_key_full
    n = p * q
    return pow(message, d, n)


def Verify(message, signature, public_key):
    """Перевірка підпису: M == S^e mod n"""
    n, e = public_key
    decrypted_signature = pow(signature, e, n)
    return decrypted_signature == message