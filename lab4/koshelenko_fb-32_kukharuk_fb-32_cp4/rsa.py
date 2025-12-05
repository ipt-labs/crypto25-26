import random
from math import gcd

# Евклід
def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a, mod):
    g, x, _ = egcd(a, mod)
    if g != 1:
        return None
    return x % mod

# modpow
def modpow(base, exp, mod):
    r = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            r = (r * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return r

# Miller-Rabin
small_primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,
                53,59,61,67,71,73,79,83,89,97]

def trial_division(n):
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False
    return True

def miller_rabin(n, k=20):
    if n < 2:
        return False
    if not trial_division(n):
        return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = modpow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        ok = False
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                ok = True
                break
        if not ok:
            return False
    return True

def random_prime(bits=256):
    while True:
        x = random.getrandbits(bits)
        x |= (1 << (bits - 1)) | 1
        if miller_rabin(x):
            return x

# RSA
def GenerateKeyPair(bits=256):
    p = random_prime(bits)
    q = random_prime(bits)
    while q == p:
        q = random_prime(bits)
    n = p * q
    phi = (p - 1)*(q - 1)
    while True:
        e = random.randrange(2**16, phi - 1)
        if gcd(e, phi) == 1:
            break
    d = mod_inverse(e, phi)
    return (e, n), (d, p, q)

def Encrypt(M, pub):
    e, n = pub
    return modpow(M, e, n)

def Decrypt(C, priv):
    d, p, q = priv
    return modpow(C, d, p*q)

def Sign(M, priv):
    d, p, q = priv
    return modpow(M, d, p*q)

def Verify(M, S, pub):
    e, n = pub
    return M == modpow(S, e, n)

def text_to_int(t):
    return int.from_bytes(t.encode("utf-8"), "big")

def int_to_text(v):
    return v.to_bytes((v.bit_length()+7)//8, "big").decode("utf-8", errors="ignore")

def to_hex(v):
    return hex(v)[2:].upper()

# умова n_A ≤ n_B
while True:
    public_A, private_A = GenerateKeyPair()
    public_B, private_B = GenerateKeyPair()
    eA, nA = public_A
    eB, nB = public_B
    if nA <= nB:
        break

dA, pA, qA = private_A
dB, pB, qB = private_B

# генеруємо ключі
print("\n================ ГЕНЕРАЦІЯ КЛЮЧІВ =================\n")

print("[ Абонент A ]")
print("e_A =", eA)
print("n_A =", nA)
print("d_A =", dA)
print("p_A =", pA)
print("q_A =", qA)
print("\nHEX:")
print("n_A HEX =", to_hex(nA))
print("e_A HEX =", to_hex(eA))
print("d_A HEX =", to_hex(dA))

print("\n[ Абонент B ]")
print("e_B =", eB)
print("n_B =", nB)
print("d_B =", dB)
print("p_B =", pB)
print("q_B =", qB)
print("\nHEX:")
print("n_B HEX =", to_hex(nB))
print("e_B HEX =", to_hex(eB))
print("d_B HEX =", to_hex(dB))

# шифрування
print("\n================ ШИФРУВАННЯ =================\n")

msg = "NikitaIrynaCP4"
M = text_to_int(msg)
cipher = Encrypt(M, public_A)
cipher_hex = to_hex(cipher)

print("M як число =", M)
print("Шифртекст =", cipher)
print("Шифртекст HEX =", cipher_hex)

dec = Decrypt(cipher, private_A)
print("Розшифровано =", int_to_text(dec))

# підпис
print("\n================ ПІДПИС RSA =================\n")

sig = Sign(M, private_A)
sig_hex = to_hex(sig)

print("Підпис =", sig)
print("Підпис HEX =", sig_hex)
print("Перевірка =", Verify(M, sig, public_A))

# протокол
print("\n================ ПРОТОКОЛ A → B =================\n")

k = random.randint(2, nA - 1)
C1 = Encrypt(k, public_B)
S1 = Sign(k, private_A)

k_recv = Decrypt(C1, private_B)
valid = Verify(k_recv, S1, public_A)

print("k =", k)
print("C1 =", C1)
print("S1 =", S1)
print("Отриманий k' =", k_recv)
print("Перевірка підпису =", valid)
