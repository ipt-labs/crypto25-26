from random import randrange
from math import gcd
import hashlib

#розширений Евклід + інверсія
def gcd_extended(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = gcd_extended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y

def find_reverse(a, mod):
    g, x, _ = gcd_extended(a, mod)
    if g == 1:
        return (x % mod + mod) % mod
    return -1

#міллер–рабін + пробні ділення
_small_primes = [
    2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,
    67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,
    139,149,151,157,163,167,173,179,181,191,193,197,199
]

def miller_rabin(n, rounds=16):
    if n < 2:
        return False
    for p in _small_primes:
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
        a = randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

#генерація простих і пар
def gen_prime(bits):
    while True:
        cand = randrange(1 << (bits - 1), 1 << bits) | 1
        if miller_rabin(cand):
            return cand

def gen_numbers_pair():
    while True:
        p, q, p1, q1 = gen_prime(256), gen_prime(256), gen_prime(256), gen_prime(256)
        if len({p, q, p1, q1}) < 4:
            continue
        if p * q < p1 * q1:
            return p, q, p1, q1

#ключі RSA
def GenerateKeyPair(p, q, e=65537):
    n = p * q
    phi = (p - 1) * (q - 1)
    while gcd(e, phi) != 1:
        e += 2
    d = find_reverse(e, phi)
    return [e, n], [d, p, q]

#хеш для підпису
def hex_from_int(m_int):
    blen = (m_int.bit_length() + 7) // 8
    m_bytes = m_int.to_bytes(blen, 'big')
    h = hashlib.sha256(m_bytes).digest()
    return int.from_bytes(h, 'big')

#oсновні операції RSA
def Encrypt(msg, public_key):
    e, n = public_key
    return pow(msg, e, n)

def Decrypt(cipher, private_key):
    d, p, q = private_key
    n = p * q
    return pow(cipher, d, n)

def Sign(msg, private_key):
    d, p, q = private_key
    n = p * q
    h = hex_from_int(msg)
    return pow(h, d, n)

def Verify(msg, signature, public_key):
    e, n = public_key
    h = hex_from_int(msg)
    return pow(signature, e, n) == h

#протокол обміну ключем
def SendKey(k, recipient_public, sender_private):
    k1 = Encrypt(k, recipient_public)
    s = Sign(k, sender_private)
    s1 = Encrypt(s, recipient_public)
    return k1, s1

def ReceiveKey(k1, s1, recipient_private, sender_public, file):
    k = Decrypt(k1, recipient_private)
    s = Decrypt(s1, recipient_private)
    if Verify(k, s, sender_public):
        file.write(f"message k = {k}\nsignature confirmed\n\n")
    else:
        file.write("signature not confirmed\n\n")
    return k, s

#тест
def my_test():
    with open("rsa_output.txt", "w", encoding="utf-8") as out:

        p, q, p1, q1 = gen_numbers_pair()
        out.write(f"p = {p}\nq = {q}\np1 = {p1}\nq1 = {q1}\n\n")

        pub_A, priv_A = GenerateKeyPair(p, q)
        pub_B, priv_B = GenerateKeyPair(p1, q1)

        out.write("abonent А:\n")
        out.write(f"public key (e, n): {pub_A}\n")
        out.write(f"private key (d, p, q): {priv_A}\n\n")
        out.write("abonent В:\n")
        out.write(f"public key (e, n): {pub_B}\n")
        out.write(f"private key (d, p, q): {priv_B}\n\n")

        msg = 12345678901234567890

        out.write("abonent A\n")
        enc_A = Encrypt(msg, pub_A)
        dec_A = Decrypt(enc_A, priv_A)
        sig_A = Sign(msg, priv_A)
        out.write(f"encrypted: {enc_A}\ndecrypted: {dec_A}\n")
        out.write(f"signature: {sig_A}\ncheck: {Verify(msg, sig_A, pub_A)}\n\n")

        out.write("abonent B\n")
        enc_B = Encrypt(msg, pub_B)
        dec_B = Decrypt(enc_B, priv_B)
        sig_B = Sign(msg, priv_B)
        out.write(f"encrypted: {enc_B}\ndecrypted: {dec_B}\n")
        out.write(f"signature: {sig_B}\ncheck: {Verify(msg, sig_B, pub_B)}\n\n")

        # Протокол обміну
        out.write("exhange protool (А -> В)\n")
        k1, s1 = SendKey(msg, pub_B, priv_A)
        ReceiveKey(k1, s1, priv_B, pub_A, out)


if __name__ == '__main__':
    my_test()