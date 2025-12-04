import random
from rsa_core import GenerateKeyPair, Encrypt, Decrypt, Sign, Verify
from rsa_protocol import SendKey, ReceiveKey

def main():
    print("[1] Генерація ключів для абонентів А і В...")

    priv_A, pub_A = GenerateKeyPair(256)
    print(f"   A Public Key (n, e): ({pub_A[0]}, {pub_A[1]})")

    priv_B, pub_B = GenerateKeyPair(256)

    while pub_B[0] < pub_A[0]:
        print("   (Перегенерація ключів В для виконання умови n_B >= n_A)...")
        priv_B, pub_B = GenerateKeyPair(256)

    print(f"   B Public Key (n1, e1): ({pub_B[0]}, {pub_B[1]})")

    print("\n[2] Тест шифрування/розшифрування (Confidentiality)")
    message = 123456789
    print(f"   Відкрите повідомлення: {message}")

    cipher_text = Encrypt(message, pub_A)
    print(f"   Зашифроване (C): {cipher_text}")

    decrypted_msg = Decrypt(cipher_text, priv_A)
    print(f"   Розшифроване (M): {decrypted_msg}")

    if message == decrypted_msg:
        print("   >>> Статус: Успішно")

    print("\n[3] Тест цифрового підпису (Integrity & Authentication)")
    msg_to_sign = 987654321
    print(f"   Повідомлення для підпису: {msg_to_sign}")

    signature = Sign(msg_to_sign, priv_A)
    print(f"   Підпис А (S): {signature}")

    is_valid = Verify(msg_to_sign, signature, pub_A)
    print(f"   Результат перевірки підпису: {is_valid}")

    if is_valid:
        print("   >>> Статус: Підпис вірний")
    else:
        print("   >>> Статус: Підпис НЕ вірний")

    print("\n[4] Протокол конфіденційного розсилання ключів (А -> В)")

    k = random.randrange(1, pub_A[0])
    print(f"   Секретний ключ k, що передається: {k}")

    package = SendKey(k, priv_A, pub_A, pub_B)
    print(f"   Відправлено пакет (k1, S1): {package}")

    received_k, auth_valid = ReceiveKey(package, priv_B, pub_A)

    print(f"   Отримано k: {received_k}")
    print(f"   Автентифікація підтверджена: {auth_valid}")

    if k == received_k and auth_valid:
        print("   >>> Висновок: Протокол виконано успішно.")
    else:
        print("   >>> Висновок: Помилка протоколу.")


if __name__ == "__main__":
    main()