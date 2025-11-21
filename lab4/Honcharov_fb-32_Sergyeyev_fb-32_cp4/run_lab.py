import random

from rsa_core import (
    GenerateKeyPair, 
    Encrypt, 
    Decrypt, 
    Sign, 
    Verify, 
    SendKey, 
    ReceiveKey
)

BIT_LENGTH = 256 

print(f"--- Генерація ключів (біт: {BIT_LENGTH}) ---")

print("Генерація ключів для Абонента А...")
(n_A, e_A), (d_A, p_A, q_A) = GenerateKeyPair(BIT_LENGTH)
print("Генерація ключів для Абонента B...")
(n_B, e_B), (d_B, p_B, q_B) = GenerateKeyPair(BIT_LENGTH)

while n_B < n_A:
    print("n_B < n_A, перегенерація ключів B...")
    (n_B, e_B), (d_B, p_B, q_B) = GenerateKeyPair(BIT_LENGTH)

print("\nПараметри RSA Абонента A:")
print(f"  p_A = {p_A}")
print(f"  q_A = {q_A}")
print(f"  n_A = {n_A}")
print(f"  e_A = {e_A}")
print(f"  d_A = {d_A}")
print("\nПараметри RSA Абонента B:")
print(f"  p_B = {p_B}")
print(f"  q_B = {q_B}")
print(f"  n_B = {n_B}")
print(f"  e_B = {e_B}")
print(f"  d_B = {d_B}")
print("-----------------------------------------")

print("\n--- Тест шифрування/розшифрування ---")

M = random.randint(1, n_A - 1)
print(f"Відкритий текст M = {M}")

C = Encrypt(M, (n_B, e_B))
print(f"Шифротекст для B: C = {C}")

M_A_decrypted = Decrypt(C, (d_B, p_B, q_B))
print(f"B розшифровує C: M' = {M_A_decrypted}")

if M == M_A_decrypted:
    print("УСПІХ: M == M'")
else:
    print("ПОМИЛКА: M != M'")
print("-----------------------------------------")

print("\n--- Тест Цифрового Підпису ---")
message_text = "aboba"
print(f"Відкритий текст: '{message_text}'")

signature_A = Sign(message_text, (d_A, p_A, q_A))
print(f"Підпис Абонента А: S_A = {signature_A}")

is_valid = Verify("aboba", signature_A, (n_A, e_A))
print(f"Абонент B проверил підпис: {is_valid}")
print("-----------------------------------------")

print("\n--- Тест протокола розсилки ключів ---")

k_secret = random.randint(1, n_A - 1) 
print(f"Абонент А генерує секретне значення k = {k_secret}")

k1_S1_pair = SendKey(k_secret, (d_A, p_A, q_A), (n_B, e_B))
print(f"А відправляє пару (k1, S1): ({k1_S1_pair[0]}, {k1_S1_pair[1]})")

k_received, auth_status = ReceiveKey(k1_S1_pair, (d_B, p_B, q_B), (n_A, e_A))

print(f"Абонент B отримав значення k' = {k_received}")
print(f"Статус автентифікації: {auth_status}")

if k_secret == k_received and auth_status:
    print("УСПІХ: Протокол виконаний, ключі співпадають і автентифікація пройдена.")
else:
    print("ПОМИЛКА: Протокол не виконаний.")