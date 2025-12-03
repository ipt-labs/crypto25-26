from vigenere import encrypt, decrypt, alh
from analysis import method1, method2, find_key

with open("text.txt", "r", encoding="utf8") as file:
    cipher_text = file.read()
    cipher_text = ''.join(c for c in cipher_text if c in alh)

print("Method 1:")
method1(cipher_text)

print("\nMethod 2:")
method2(cipher_text)

print("\nKey search:")
r = 14
key = find_key(cipher_text, r)
print(f"r={r}, key: {key}")

plain = decrypt(cipher_text, key)
print(f"Decrypted: {plain[:100]}")

key = 'последнийдозор'
plain = decrypt(cipher_text, key)
print(f"\nkey: {key}")
print(f"Decrypted: {plain[:200]}")

with open("decrypted.txt", "w", encoding="utf8") as file:
    file.write(plain)
