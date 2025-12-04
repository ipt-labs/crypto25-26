#!/usr/bin/env python3
import requests
import json
from lab4_123 import generate_and_check_primes, KeyPair, BIT_LENGTH
from lab4_4 import Encrypt, Decrypt, Sign, Verify

SERVER_BASE_URL = "http://asymcryptwebservice.appspot.com/rsa/"
S = "[*]"

def str_to_int(s: str) -> int:
    return int.from_bytes(s.encode('utf-8'), 'big')


def int_to_str(i: int, min_len: int = 1) -> str:
    byte_length = max((i.bit_length() + 7) // 8, min_len)
    data = i.to_bytes(byte_length, 'big')
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return f"[Non-text data: {data.hex()}]"


def int_to_bytes(i: int) -> bytes:
    byte_length = (i.bit_length() + 7) // 8
    return i.to_bytes(byte_length or 1, 'big')


def serverGetKey(session: requests.Session, keySize=BIT_LENGTH) -> tuple[int, int]:
    print(f"\n{S} Отримання відкритого ключа Сервера (size={keySize})...")
    resp = session.get(f"{SERVER_BASE_URL}serverKey?keySize={keySize}")
    serverKey = json.loads(resp.content.decode("utf-8"))

    serv_n = int(serverKey['modulus'], 16)
    serv_e = int(serverKey['publicExponent'], 16)
    print(f"{S} Ключ Сервера (B) отримано: N_B={serv_n.bit_length()} bits, e_B={serv_e}")
    return serv_e, serv_n 

def test_server_encrypt(session: requests.Session, keys_A: KeyPair, message: str) -> bool:
    print("\n--- [A. ТЕСТ: Сервер Encrypt -> Локальний Decrypt] ---")
    mod_hex = bytes.hex(int_to_bytes(keys_A.n))
    exp_hex = bytes.hex(int_to_bytes(keys_A.e))

    print(f"{S} Надсилаємо M='{message}' та (e_A, n_A) на Сервер для шифрування...")
    resp = session.get(
        f"{SERVER_BASE_URL}encrypt?modulus={mod_hex}&publicExponent={exp_hex}&message={message}&type=TEXT")
    encrypted_server_response = json.loads(resp.content.decode('utf-8'))

    C_server = int(encrypted_server_response['cipherText'], 16)
    print(
        f"{S} Сервер повернув C_server: {encrypted_server_response['cipherText'][:20]}...")

    M_decrypted = Decrypt(C_server, keys_A.d, keys_A.n)
    M_recovered_str = int_to_str(M_decrypted)

    print(f"{S} Локально розшифровано (Decrypt): '{M_recovered_str}'")
    return message == M_recovered_str


def test_server_decrypt(session: requests.Session, keys_B_server: tuple[int, int], message: str) -> bool:
    print("\n--- [B. ТЕСТ: Локальний Encrypt -> Сервер Decrypt] ---")
    e_B, n_B = keys_B_server

    M_val = str_to_int(message)
    C_local = Encrypt(M_val, e_B, n_B)
    enc_hex = bytes.hex(int_to_bytes(C_local))
    print(f"{S} Локально зашифровано (Encrypt): C_local={enc_hex[:20]}...")

    print(f"{S} Надсилаємо C_local на Сервер для розшифрування...")
    resp = session.get(
        f"{SERVER_BASE_URL}decrypt?cipherText={enc_hex}&expectedType=TEXT")
    decrypted_server_response = json.loads(resp.content.decode('utf-8'))

    print(f"{S} Сервер розшифрував: {decrypted_server_response}")
    return message == decrypted_server_response.get('message')


def test_local_sign_server_verify(session: requests.Session, keys_A: KeyPair, message: str) -> bool:
    print("\n--- [C. ТЕСТ: Локальний Sign -> Сервер Verify] ---")
    mod_hex = bytes.hex(int_to_bytes(keys_A.n))
    exp_hex = bytes.hex(int_to_bytes(keys_A.e))
    M_val = str_to_int(message)
    S_local = Sign(M_val, keys_A.d, keys_A.n)
    sig_hex = bytes.hex(int_to_bytes(S_local))
    print(f"{S} Локально створено підпис (Sign): S_local={sig_hex[:20]}...")
    print(f"{S} Надсилаємо M, S_local та (e_A, n_A) на Сервер для перевірки...")
    resp = session.get(
        f"{SERVER_BASE_URL}verify?message={message}&signature={sig_hex}&modulus={mod_hex}&publicExponent={exp_hex}&type=TEXT")
    verified_server_response = json.loads(resp.content.decode('utf-8'))
    print(f"{S} Сервер перевірив: {verified_server_response}")
    return verified_server_response.get('verified') == True


def test_server_sign_local_verify(session: requests.Session, keys_A: KeyPair, keys_B_server: tuple[int, int], message: str) -> bool:
    print("\n--- [D. ТЕСТ: Сервер Sign -> Локальний Verify] ---")
    e_B, n_B = keys_B_server
    print(f"{S} Просимо Сервер підписати M='{message}'...")
    resp = session.get(f"{SERVER_BASE_URL}sign?message={message}&type=TEXT")
    signature_server_response = json.loads(resp.content.decode('utf-8'))
    S_server = int(signature_server_response['signature'], 16)
    print(
        f"{S} Сервер повернув S_server: {signature_server_response['signature'][:20]}...")

    M_val = str_to_int(message)
    is_verified_local = Verify(M_val, S_server, e_B, n_B)
    print(f"{S} Локальна перевірка (Verify): {is_verified_local}")
    return is_verified_local

def main():
    print("--- ЗАВДАННЯ 4: Двостороння перевірка коректності операцій ---")
    s = requests.Session()
    print("\n[КРОК 1: Генерація локальних ключів (A)]")
    keys_A, _ = generate_and_check_primes()

    try:
        print("\n[КРОК 2: Отримання ключів Сервера (B)]")
        keys_B_server = serverGetKey(s, keySize=BIT_LENGTH) 
        test_message_str = 'Hello World!'
        print(f"\n[КРОК 3: Запуск 4 тестів сумісності]")

        test_A_ok = test_server_encrypt(s, keys_A, test_message_str)
        test_B_ok = test_server_decrypt(s, keys_B_server, test_message_str)
        test_C_ok = test_local_sign_server_verify(s, keys_A, test_message_str)
        test_D_ok = test_server_sign_local_verify(s, keys_A, keys_B_server, test_message_str)

        print("\n--- ЗАГАЛЬНИЙ РЕЗУЛЬТАТ ПЕРЕВІРКИ ---")
        print(
            f"  Перевірка Decrypt (A): {'Успіх' if test_A_ok else 'Помилка'}")
        print(
            f"  Перевірка Encrypt (B): {'Успіх' if test_B_ok else 'Помилка'}")
        print(
            f"  Перевірка Sign (C):    {'Успіх' if test_C_ok else 'Помилка'}")
        print(
            f"  Перевірка Verify (D):  {'Успіх' if test_D_ok else 'Помилка'}")

    except requests.exceptions.ConnectionError:
        print(
            "\nПОМИЛКА: Не вдалося підключитися до http://asymcryptwebservice.appspot.com/")
        print("Будь ласка, перевірте підключення до Інтернету.")
    except Exception as e:
        print(f"\nВиникла помилка під час зовнішньої перевірки: {e}")


if __name__ == "__main__":
    main()
