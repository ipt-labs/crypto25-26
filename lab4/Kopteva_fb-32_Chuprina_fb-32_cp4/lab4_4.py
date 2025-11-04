import random
from typing import Tuple
from lab4_123 import mod_pow, generate_and_check_primes, KeyPair, BIT_LENGTH

def Encrypt(M: int, e: int, n: int) -> int:
    if M >= n:
        raise ValueError("Повідомлення M має бути менше модуля n.")
    return mod_pow(M, e, n)

def Decrypt(C: int, d: int, n: int) -> int:
    return mod_pow(C, d, n)

def Sign(M: int, d: int, n: int) -> int:
    return mod_pow(M, d, n)

def Verify(M: int, S: int, e: int, n: int) -> bool:
    M_recovered = mod_pow(S, e, n)
    return M == M_recovered

if __name__ == '__main__':
    keys_A, keys_B = generate_and_check_primes()

    n_min = min(keys_A.n, keys_B.n)
    M_test = random.getrandbits(BIT_LENGTH) % n_min
    
    print("\n--- Шифрування, розшифрування, створення цифрового підпису, перевірка цифрового підпису (Завдання 4) ---")
    print(f"Оригінальне повідомлення M: {M_test}")

    print("\n--- 1. ШИФРУВАННЯ/РОЗШИФРУВАННЯ (A -> B) ---")

    C = Encrypt(M_test, keys_B.e, keys_B.n)
    print(f"Криптограма C (для B): {C}")

    M_decrypted = Decrypt(C, keys_B.d, keys_B.n)
    print(f"M (розшифровано): {M_decrypted}")
    
    is_decrypt_ok = M_test == M_decrypted
    print(f"Перевірка розшифрування: {is_decrypt_ok}")

    print("\n--- 2. ЦИФРОВИЙ ПІДПИС (A підписує) ---")
    
    S = Sign(M_test, keys_A.d, keys_A.n)
    print(f"Підпис S: {S}")
    
    is_verified = Verify(M_test, S, keys_A.e, keys_A.n)
    
    print(f"Перевірка підпису: {is_verified}")
    
    if not is_verified or not is_decrypt_ok:
        print("\nПОМИЛКА: Одна з криптографічних операцій дала збій!")
