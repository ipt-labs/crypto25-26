import os
from collections import Counter
PLAINTEXT_PATH = "harry_potter_5.txt"

RUS_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
ALPHABET_SIZE = len(RUS_ALPHABET)
alphabet_index = {ch: i for i, ch in enumerate(RUS_ALPHABET)}

KEYS = {
    "len2_ки": "ки",
    "len3_дом": "дом",
    "len4_вода": "вода",
    "len5_гарри": "гарри",
    "len12_волшебникино": "волшебникино"
}

def normalize_text(raw_text: str) -> str:
    text = ''.join(ch for ch in raw_text.lower() if ch in RUS_ALPHABET)
    return text

def index_of_coincidence(text: str) -> float:
    N = len(text)
    if N < 2:
        return 0.0
    counts = Counter(text)
    numerator = sum(n * (n - 1) for n in counts.values())
    denominator = N * (N - 1)
    return numerator / denominator

def vigenere_encrypt(text: str, key: str) -> str: 
    cipher = []
    k = len(key)
    for i, ch in enumerate(text):
        if ch not in alphabet_index:
            cipher.append(ch)
            continue
        shift = alphabet_index[key[i % k]]
        enc_index = (alphabet_index[ch] + shift) % ALPHABET_SIZE
        cipher.append(RUS_ALPHABET[enc_index])
    return ''.join(cipher)

def main():
    with open(PLAINTEXT_PATH, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()
    plaintext = normalize_text(raw_text)
    plaintext = plaintext[:3000]
    print(" Довжина очищеного відкритого тексту:", len(plaintext), "символів")
    print(" Перші 300 символів очищеного відкритого тексту:\n", plaintext[:300], "\n")
    ic_plain = index_of_coincidence(plaintext)
    print(f"I(Y) відкритий текст = {ic_plain:.6f}")
    results = []
    ciphertexts = {}

    for key_name, key_value in KEYS.items():
        cipher = vigenere_encrypt(plaintext, key_value)
        ciphertexts[key_name] = cipher
        ic_c = index_of_coincidence(cipher)
        results.append((key_name, key_value, len(key_value), ic_c))
    print("\n Приклади шифртекстів ")
    for key_name, cipher in ciphertexts.items():
        print(f"[{key_name}] {cipher[:200]}\n")
    print(" Порівняння індексу відповідності I(Y) ")
    print("{:<20} {:<20} {:<10} {:<15}".format(
        "Позначення ключа", "Ключ", "Довжина", "I(Y) шифртексту"))
    print("-" * 70)
    for key_name, key_value, klen, ic_c in results:
        print("{:<20} {:<20} {:<10} {:<15.6f}".format(
            key_name, key_value, klen, ic_c))
    print("\n I(Y) відкритий текст =", f"{ic_plain:.6f}")

if __name__ == "__main__":
    main()
