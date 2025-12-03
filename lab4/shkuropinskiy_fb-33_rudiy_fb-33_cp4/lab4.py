import random

def extended_euclid(a, b):
    if b == 0:
        return a, 1, 0
    d, u, v = extended_euclid(b, a % b)
    return d, v, u - (a // b) * v


def is_prime(p, k=5):
    if p <= 1 or p % 2 == 0:
        return False
    d = p - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        a = random.randint(2, p - 2)
        gcd, _, _ = extended_euclid(a, p)
        if gcd > 1:
            return False

        x = pow(a, d, p)
        if x == 1 or x == p - 1:
            continue

        for _ in range(r - 1):
            x = pow(x, 2, p)
            if x == p - 1:
                break
            if x == 1:
                return False
        else:
            return False
    return True


def generate_prime(length):
    lower = 1 << (length - 1)
    higher = (1 << length) - 1
    failed_candidates = []
    while True:
        prime_candidate = random.randint(lower, higher)
        if is_prime(prime_candidate):
            if failed_candidates:
                print(f"Кандидати, що не пройшли перевірку простоти: {failed_candidates} (кількість {len(failed_candidates)})")
            return prime_candidate
        else:
            failed_candidates.append(prime_candidate)


def GenerateKeyPair(length=256):
    p = generate_prime(length)
    q = generate_prime(length)
    n = p * q
    fi_n = (p - 1) * (q - 1)

    e = random.randint(2, fi_n - 1)
    while extended_euclid(e, fi_n)[0] != 1:
        e = random.randint(2, fi_n - 1)

    d = extended_euclid(e, fi_n)[1] % fi_n

    public_key = (n, e)
    secret_key = (d, p, q)

    return public_key, secret_key, n

def Encrypt(text, e, n):
    return pow(text, e, n)

def Decrypt(cyphertext, d, n):
    return pow(cyphertext, d, n)

def Sign(message, d, n):
    return pow(message, d, n)

def VerifySignature(message, signature, e, n):
    return message == pow(signature, e, n)

def SendKey(message, sender_public, sender_private, receiver_public):
    signature = Sign(message, sender_private, sender_public[0])
    encrypted_signature = Encrypt(signature, receiver_public[1], receiver_public[0])
    encrypted_message = Encrypt(message, receiver_public[1], receiver_public[0])
    return encrypted_message, encrypted_signature


def ReceiveKey(encrypted_message, encrypted_signature, sender_public, receiver_private, receiver_public):
    message = Decrypt(encrypted_message, receiver_private, receiver_public[0])
    signature = Decrypt(encrypted_signature, receiver_private, receiver_public[0])
    return VerifySignature(message, signature, sender_public[1], sender_public[0])


pub_A, sec_A, n_A = GenerateKeyPair(length=256)
pub_B, sec_B, n_B = GenerateKeyPair(length=256)

if n_A > n_B:
    pub_A, pub_B = pub_B, pub_A
    sec_A, sec_B = sec_B, sec_A
    n_A, n_B = n_B, n_A

message = random.randint(1, min(n_A, n_B) - 1) 

print("Генерація RSA ключів")

print("Ключі абонента A:")
print("Public Key:")
print(f"  n = {pub_A[0]}")
print(f"  e = {pub_A[1]}")
print("Private Key:")
print(f"  d = {sec_A[0]}")
print(f"  p = {sec_A[1]}")
print(f"  q = {sec_A[2]}\n")

print("Ключі абонента B:")
print("Public Key:")
print(f"  n = {pub_B[0]}")
print(f"  e = {pub_B[1]}")
print("Private Key:")
print(f"  d = {sec_B[0]}")
print(f"  p = {sec_B[1]}")
print(f"  q = {sec_B[2]}\n")

print("Початкове повідомлення")
print(f"Message = {message}\n")

encrypted_message, encrypted_signature = SendKey(message, sender_public=pub_A, sender_private=sec_A[0], receiver_public=pub_B)

signature = Sign(message, sec_A[0], pub_A[0])

print("A -> B: підпис і шифрування")


print("Підпис (S = M^d mod n_A):")
print(f"Signature (до шифрування): {signature}\n")

print("Шифрування повідомлення (Encrypt(M, e_B, n_B)):")
print(f"Encrypted message: {encrypted_message}\n")

print("Шифрування підпису (Encrypt(S, e_B, n_B)):")
print(f"Encrypted signature: {encrypted_signature}\n")

is_valid = ReceiveKey(encrypted_message, encrypted_signature, sender_public=pub_A, receiver_private=sec_B[0], receiver_public=pub_B)

print("B приймає повідомлення і перевіряє підпис")

print(f"Розшифроване повідомлення: {message}")
print(f"Перевірка підпису: {is_valid}")

print("Обмін завершено")
