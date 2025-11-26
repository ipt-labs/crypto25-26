from mod import Horner
from RSA_key import generate_rsa_keys
import random

def RSA_Encrypt(plaintext, public_key):
    n, e = public_key
    if not isinstance(plaintext, int):
        plaintext = int.from_bytes(plaintext.encode('utf-8'), byteorder='big')  # Конвертація у ціле число
    return Horner(plaintext, e, n)

def RSA_Decrypt(ciphertext, private_key):
    d, p, q = private_key
    n = p * q
    decrypted_int = Horner(ciphertext, d, n)
    return decrypted_int

def RSA_Sign(plaintext, private_key):
    d, p, q = private_key
    n = p * q
    if not isinstance(plaintext, int):
        plaintext = int.from_bytes(plaintext.encode('utf-8'), byteorder='big') # Конвертація у ціле число
    return Horner(plaintext, d, n)

def RSA_Verify(signature, public_key, plaintext):
    n, e = public_key
    if not isinstance(plaintext, int):
        plaintext = int.from_bytes(plaintext.encode('utf-8'), byteorder='big')  # Конвертація у ціле число
    verified_value = Horner(signature, e, n)  
    print(f"Підпис відновлюється в {verified_value}, очікуване: {plaintext}")
    return verified_value == plaintext

def RSA_SendKey(k, public_key_b, private_key_a):
    """
    Відправка ключа від A до B.
    k: значення ключа
    public_key_b: відкритий ключ отримувача B
    private_key_a: секретний ключ відправника A
    """
    k1 = RSA_Encrypt(k, public_key_b)   # k1 = k^e1 mod n1
    S = RSA_Sign(k, private_key_a)      # S = k^d mod n
    S1 = RSA_Encrypt(S, public_key_b)   # S1 = S^e1 mod n1

    print(f"Зашифрований ключ (k1): {hex(k1)}")
    print(f"Зашифрований підпис (S1): {hex(S1)}")

    return k1, S1

def RSA_ReceiveKey(k1, S1, private_key_b, server_public_key):
    """
    Реалізація роботи приймача B.
    k1: зашифроване значення k
    S1: зашифрований підпис S
    private_key_b: секретний ключ абонента B (d1, n1)
    server_public_key: відкритий ключ абонента A (e, n)
    """
    k_dec = RSA_Decrypt(k1, private_key_b)  # k = k1^d1 mod n1
    S_dec = RSA_Decrypt(S1, private_key_b)  # S = S1^d1 mod n1

    k_verify = RSA_Verify(S_dec, server_public_key, k_dec)# k_verify = S^e mod n

    return k_dec, k_verify

if __name__ == "__main__":
    # Задання ключів і повідомлення
    hex_key = "92795D979FBB6B83223B7560EFDD548A456C95FDF30980CD4BB67A4927F305DD"
    n_a = int(hex_key, 16)  # Перетворення 256-бітного ключа з шістнадцяткового формату
    e = int('10001', 16)
    plaintext = 'hello'
    server_public_key = (n_a, e)

    # Власні ключі
    p  = 299157106990053262012411451524571409563
    q  = 217256719530941090911950897117559777241
    public_key, private_key = generate_rsa_keys(p, q)
    print(f"public_key у hex форматі: (n: {hex(public_key[0])}, e: {hex(public_key[1])})")

    y = int('67BE8FCE5E0643E219089F52D8AD18D6EED045DCCDB151593D8FC6C40EA68815', 16)
    # Шифрування
    print("\n=== Шифрування ===")
    ciphertext = RSA_Encrypt(plaintext, server_public_key)
    print(f"Оригінальне повідомлення (plaintext): {plaintext}")
    print(f"Шифротекст власний: {ciphertext}")
    print(f"Шифротекст сервер: {y}")
    
    print("\n=== Розшифрування ===")
    ciphertext =  int('3B4589EE11B64D448A3FA7AC0BAA879692873C841F947198268A6626C0535078', 16)
    print(f"Оригінальне повідомлення (plaintext): {plaintext}")
    print(f"Шифротекст: {ciphertext}")
    decrypted = RSA_Decrypt(ciphertext, private_key)
    print(f"Розшифрований: {decrypted.to_bytes((decrypted.bit_length() + 7) // 8, byteorder='big').decode('utf-8')}")

    print("\n=== Перевірка підпису ===")
    signature = int('171724600AA21AAF590E9E66645B393FCA87DE673B5F9B9C6EA3955855946B6C', 16)
    verified = RSA_Verify(signature, server_public_key, plaintext)
    print(f"Підпис коректний: {verified}")

    print("\n=== Цифровий підпис ===")
    signature = RSA_Sign(plaintext, private_key)
    print(f"Цифровий підпис (signature): {signature}")
    print(f"Цифровий підпис у hex форматі: {hex(signature)}")
    print(f"public_key у hex форматі: (n: {hex(public_key[0])}, e: {hex(public_key[1])})")

    k1 = int('5EBB49656302C83D4BFFFD08DB229EC17E9CA397385FDBAB2126AE29268C7CAE', 16)
    S1 = int('03BA3C5565470A54B10692AD458141BEC740652C3E3B00171963CCC30A34E846', 16)
    
    print("\n=== Receive ===")
    k_dec, k_verify = RSA_ReceiveKey(k1, S1, private_key, server_public_key)
    print(f"Розшифрований абонентом В k: {k_dec, k_verify}")
    print(f"Перевірка підпису А пройшла успішно: {k_verify}")

    _, n = public_key
    k = random.randint(1, n - 1)
    print("\n=== Send ===")
    k1, S1 = RSA_SendKey(k, server_public_key, private_key)


