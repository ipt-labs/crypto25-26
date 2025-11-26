from RSA_key import generate_rsa_keys
from mod import Horner
from random_prime import generate_prime_pairs
import random

def RSA_Encrypt(plaintext, public_key):
    n, e = public_key
    return Horner(plaintext, e, n)

def RSA_Decrypt(ciphertext, private_key):
    d, p, q = private_key
    n = p * q
    return Horner(ciphertext, d, n)

def RSA_Sign(plaintext, private_key):
    d, p, q = private_key
    n = p * q
    return Horner(plaintext, d, n)

def RSA_Verify(signature, public_key, plaintext):
    n, e = public_key
    verified_value = Horner(signature, e, n)  
    print(f"Підпис відновлюється в {verified_value}, очікуване: {plaintext}")
    return verified_value == plaintext

if __name__ == "__main__":
    bit_length = 256
    
    # Генерація простих чисел для абонента A
    primes_a = generate_prime_pairs(bit_length)
    p, q = primes_a[0][0], primes_a[0][1]

    # Генерація простих чисел для абонента B
    primes_b = generate_prime_pairs(bit_length)
    p1, q1 = primes_b[0][0], primes_b[0][1]

    # Генерація ключів для абонентів A та B
    public_key_a, private_key_a = generate_rsa_keys(p, q)
    public_key_b, private_key_b = generate_rsa_keys(p1, q1)

    # Випадкове повідомлення для шифрування
    plaintext = random.randint(1, public_key_b[0] - 1)

    # Шифрування
    print("\nШифрування")
    print("=" * 160)
    ciphertext = RSA_Encrypt(plaintext, public_key_b)
    print(f"Оригінальне повідомлення (plaintext): {plaintext}")
    print("-" * 160)
    print(f"Шифротекст (ciphertext): {ciphertext}")

    # Розшифрування
    print("\nРозшифрування")
    print("=" * 160)
    decrypted_plaintext = RSA_Decrypt(ciphertext, private_key_b)
    print(f"Розшифроване повідомлення (plaintext): {decrypted_plaintext}")

    # Цифровий підпис
    print("\nЦифровий підпис")
    print("=" * 160)
    signature = RSA_Sign(plaintext, private_key_a)
    print(f"Цифровий підпис (signature): {signature}")

    # Перевірка підпису
    print("\nПеревірка підпису")
    print("=" * 160)
    is_valid = RSA_Verify(signature, public_key_a, plaintext)
    print(f"Підпис валідний: {is_valid}")
