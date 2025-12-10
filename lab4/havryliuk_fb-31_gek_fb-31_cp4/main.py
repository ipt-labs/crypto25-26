"""
Головна програма для демонстрації роботи RSA криптосистеми
Лабораторна робота №4
Варіант 6
"""

import random
from rsa_system import (
    GenerateKeyPair, Encrypt, Decrypt, Sign, Verify, SendKey, ReceiveKey
)


def print_section_header(title: str):
    """Вивід заголовку розділу"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_key_info(name: str, key_pair):
    """Вивід інформації про ключову пару"""
    e, n = key_pair.public_key
    d, p, q = key_pair.private_key
    
    print(f"\n{name}:")
    print(f"  p = {p}")
    print(f"  q = {q}")
    print(f"  n = p*q = {n}")
    print(f"  n (біт): {n.bit_length()}")
    print(f"  e = {e}")
    print(f"  d = {d}")


def test_local_operations():
    """Тестування локальних операцій RSA між двома абонентами"""
    print_section_header("ЛОКАЛЬНЕ ТЕСТУВАННЯ RSA")
    
    # Генерація ключів для абонента А
    print("\n[1] Генерація ключової пари для абонента А...")
    keys_a = GenerateKeyPair(bits=512)
    print_key_info("Абонент А", keys_a)
    
    # Генерація ключів для абонента B
    # Перегенеровуємо доки n_B >= n_A (умова протоколу розсилання)
    print("\n[2] Генерація ключової пари для абонента B...")
    while True:
        keys_b = GenerateKeyPair(bits=512)
        if keys_b.public_key[1] >= keys_a.public_key[1]:
            break
    print_key_info("Абонент B", keys_b)
    
    # Тестування шифрування/розшифрування
    print_section_header("ТЕСТУВАННЯ ШИФРУВАННЯ ТА РОЗШИФРУВАННЯ")
    
    # Генеруємо випадкове повідомлення
    message = random.randint(1, keys_a.public_key[1] - 1)
    print(f"\nВипадкове повідомлення M = {message}")
    
    # Шифрування для А
    print("\n[1] Шифрування для абонента А:")
    e_a, n_a = keys_a.public_key
    d_a, _, _ = keys_a.private_key
    ciphertext_a = Encrypt(message, e_a, n_a)
    print(f"  Шифротекст C = {ciphertext_a}")
    decrypted_a = Decrypt(ciphertext_a, d_a, n_a)
    print(f"  Розшифроване M' = {decrypted_a}")
    print(f"  Перевірка: M == M' ? {message == decrypted_a}")
    
    # Шифрування для B
    print("\n[2] Шифрування для абонента B:")
    message_b = random.randint(1, keys_b.public_key[1] - 1)
    print(f"  Повідомлення M = {message_b}")
    e_b, n_b = keys_b.public_key
    d_b, _, _ = keys_b.private_key
    ciphertext_b = Encrypt(message_b, e_b, n_b)
    print(f"  Шифротекст C = {ciphertext_b}")
    decrypted_b = Decrypt(ciphertext_b, d_b, n_b)
    print(f"  Розшифроване M' = {decrypted_b}")
    print(f"  Перевірка: M == M' ? {message_b == decrypted_b}")
    
    # Тестування цифрового підпису
    print_section_header("ТЕСТУВАННЯ ЦИФРОВОГО ПІДПИСУ")
    
    # Підпис від А
    print("\n[1] Підпис повідомлення абонентом А:")
    msg_to_sign = random.randint(1, n_a - 1)
    print(f"  Повідомлення M = {msg_to_sign}")
    msg_a, sig_a = Sign(msg_to_sign, d_a, n_a)
    print(f"  Підпис S = {sig_a}")
    verified_a = Verify(msg_a, sig_a, e_a, n_a)
    print(f"  Перевірка підпису: {verified_a}")
    
    # Підпис від B
    print("\n[2] Підпис повідомлення абонентом B:")
    msg_to_sign_b = random.randint(1, n_b - 1)
    print(f"  Повідомлення M = {msg_to_sign_b}")
    msg_b, sig_b = Sign(msg_to_sign_b, d_b, n_b)
    print(f"  Підпис S = {sig_b}")
    verified_b = Verify(msg_b, sig_b, e_b, n_b)
    print(f"  Перевірка підпису: {verified_b}")
    
    # Тестування протоколу розсилання ключів
    print_section_header("ПРОТОКОЛ КОНФІДЕНЦІЙНОГО РОЗСИЛАННЯ КЛЮЧІВ")
    
    # А відправляє ключ B
    print("\n[1] Генерація секретного ключа та підготовка до відправки:")
    secret_key = random.randint(1, 2**63)
    print(f"  Секретний ключ k = {secret_key}")
    
    print("\n[2] Абонент А підписує та шифрує ключ для абонента B:")
    k1, s1 = SendKey(secret_key, d_a, n_a, e_b, n_b)
    print(f"  k1 (зашифрований ключ) = {k1}")
    print(f"  S1 (зашифрований підпис) = {s1}")
    
    print("\n[3] Абонент B отримує, розшифровує та перевіряє:")
    received_key, received_sig, is_verified = ReceiveKey(k1, s1, d_b, n_b, e_a, n_a)
    print(f"  Розшифрований ключ k = {received_key}")
    print(f"  Розшифрований підпис S = {received_sig}")
    print(f"  Підпис перевірено: {is_verified}")
    print(f"  Ключ коректний: {secret_key == received_key}")
    
    print_section_header("ЗАВЕРШЕННЯ ЛОКАЛЬНОГО ТЕСТУВАННЯ")
    print("\nВсі локальні операції виконано успішно!")
    
    return keys_a, keys_b


def main():
    """Головна функція"""
    print("=" * 80)
    print(" " * 20 + "ЛАБОРАТОРНА РОБОТА №4")
    print(" " * 15 + "Криптосистема RSA та цифровий підпис")
    print(" " * 30 + "Варіант 6")
    print("=" * 80)
    
    # Локальне тестування
    test_local_operations()
    
    print("\n" + "=" * 80)
    print("Програма завершена успішно!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
