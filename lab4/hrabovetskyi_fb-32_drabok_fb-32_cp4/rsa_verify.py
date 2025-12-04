from rsa_core import GenerateKeyPair, Decrypt, Sign


def main():
    print(">>> Генеруємо пару ключів...")
    priv_key, pub_key = GenerateKeyPair(256)
    n, e = pub_key

    print("\n    [1] ШИФРУВАННЯ НА САЙТІ    ")
    print(f"Modulus (n): {hex(n)[2:]}")
    print(f"Public Exponent (e): {hex(e)[2:]}")

    c_hex = input("\nCiphertext з сайту (HEX) >>> ").strip()
    if c_hex:
        try:
            decrypted = Decrypt(int(c_hex, 16), priv_key)
            print(f"Розшифровано (число): {decrypted}")
            try:
                print(f"Розшифровано (текст): {decrypted.to_bytes((decrypted.bit_length() + 7) // 8, 'big').decode()}")
            except:
                pass
        except Exception as err:
            print(f"Помилка: {err}")

    msg = "Hello World"
    sig = Sign(int.from_bytes(msg.encode('utf-8'), 'big'), priv_key)

    print("\n     [2] ПЕРЕВІРКИ ПІДПИСУ    ")
    print(f"Message (Text): {msg}")
    print(f"Signature: {hex(sig)[2:]}")
    print(f"Modulus: {hex(n)[2:]}")
    print(f"Public Exponent: {hex(e)[2:]}")


if __name__ == "__main__":
    main()