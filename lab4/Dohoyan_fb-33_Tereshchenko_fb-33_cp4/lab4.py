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
    failed_count = 0
    while True:
        prime_candidate = random.randint(lower, higher)
        if is_prime(prime_candidate):
            if failed_count > 0:
                print(f"Кількість кандидатів, що не пройшли перевірку простоти: {failed_count}")
            return prime_candidate
        else:
            failed_count += 1

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

def Encrypt(message, e, n):
    return pow(message, e, n)

def Decrypt(ciphertext, d, n):
    return pow(ciphertext, d, n)

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
    return message, VerifySignature(message, signature, sender_public[1], sender_public[0])

pub_A, sec_A, n_A = GenerateKeyPair(length=256)
pub_B, sec_B, n_B = GenerateKeyPair(length=256)

if n_A > n_B:
    pub_A, pub_B = pub_B, pub_A
    sec_A, sec_B = sec_B, sec_A
    n_A, n_B = n_B, n_A

message = random.randint(1, min(n_A, n_B) - 1)

print("\n=== ВИБРАНІ ПРОСТІ ЧИСЛА ===")
print(f"A: p = {sec_A[1]}, q = {sec_A[2]}")
print(f"B: p1 = {sec_B[1]}, q1 = {sec_B[2]}")

print("\n=== ПАРАМЕТРИ RSA ===")
print("A:")
print(f"  nA = {pub_A[0]}")
print(f"  eA = {pub_A[1]}")
print(f"  dA = {sec_A[0]}")
print("B:")
print(f"  nB = {pub_B[0]}")
print(f"  eB = {pub_B[1]}")
print(f"  dB = {sec_B[0]}")

print("\n=== ПОЧАТКОВЕ ПОВІДОМЛЕННЯ ===")
print(f"M = {message}")

encrypted_message, encrypted_signature = SendKey(message, pub_A, sec_A[0], pub_B)
signature = Sign(message, sec_A[0], pub_A[0])
decrypted_message, is_valid_signature = ReceiveKey(encrypted_message, encrypted_signature, pub_A, sec_B[0], pub_B)

print("\n=== ШИФРУВАННЯ ТА ПІДПИС ===")
print(f"Encrypted M = {encrypted_message}")
print(f"Encrypted Signature = {encrypted_signature}")
print(f"Signature (A) = {signature}")

print("\n=== РОЗШИФРУВАННЯ ТА ПЕРЕВІРКА ПІДПИСУ (B) ===")
print(f"Decrypted M = {decrypted_message}")
print(f"Signature valid = {is_valid_signature}")

print("\n=== ПРОТОКОЛ КОНФІДЕНЦІЙНОЇ РОЗСИЛАННЯ КЛЮЧІВ ===")
print(f"A обирає K = {message}")
print(f"A шифрує та підписує K для B:")
print(f"  Encrypted message = {encrypted_message}")
print(f"  Encrypted signature = {encrypted_signature}")
print(f"B розшифровує та перевіряє підпис:")
print(f"  Decrypted message = {decrypted_message}")
print(f"  Signature valid = {is_valid_signature}")

def to_hex(x):
    return hex(x)[2:].upper()

print("\n=== HEX-ПРЕДСТАВЛЕННЯ ===")

print("\n--- Ключі A (hex) ---")
print(f"pA_hex = {to_hex(sec_A[1])}")
print(f"qA_hex = {to_hex(sec_A[2])}")
print(f"nA_hex = {to_hex(pub_A[0])}")
print(f"eA_hex = {to_hex(pub_A[1])}")
print(f"dA_hex = {to_hex(sec_A[0])}")

print("\n--- Ключі B (hex) ---")
print(f"pB_hex = {to_hex(sec_B[1])}")
print(f"qB_hex = {to_hex(sec_B[2])}")
print(f"nB_hex = {to_hex(pub_B[0])}")
print(f"eB_hex = {to_hex(pub_B[1])}")
print(f"dB_hex = {to_hex(sec_B[0])}")

print("\n--- Повідомлення та підпис (hex) ---")
print(f"M_hex = {to_hex(message)}")
print(f"Encrypted_M_hex = {to_hex(encrypted_message)}")
print(f"Signature_hex = {to_hex(signature)}")
print(f"Encrypted_Sign_hex = {to_hex(encrypted_signature)}")
print(f"Decrypted_M_hex = {to_hex(decrypted_message)}")
