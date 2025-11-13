#!/usr/bin/env python3
import math
from collections import Counter
from pathlib import Path

CIPHER_FILE = Path("cipher_text_v1.txt")
OUT_DIR = Path("out")
MAX_KEY_LENGTH = 30
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = 32


MI_RUSSIAN = 0.0574
I0_UNIFORM = 1 / M
MOST_COMMON_CHAR_RU = 'о'
MOST_COMMON_NUM_RU = ALPHABET.index(MOST_COMMON_CHAR_RU)


def read_text_from_file(p: Path) -> str:
    text = p.read_bytes().decode("utf-8", "ignore").lower()
    allowed_chars = set(ALPHABET)

    return "".join(c for c in text if c in allowed_chars)


def char_to_num(char: str) -> int:
    return ALPHABET.index(char)


def num_to_char(num: int) -> str:
    return ALPHABET[num]


def index_of_coincidence(text: str) -> float:
    n = len(text)
    if n < 2:
        return 0.0

    counts = Counter(text)
    sum_nt_nt_minus_1 = 0

    for t in ALPHABET:
        Nt = counts.get(t, 0)
        sum_nt_nt_minus_1 += Nt * (Nt - 1)

    return sum_nt_nt_minus_1 / (n * (n - 1))


def split_ciphertext(ciphertext: str, r: int) -> list[str]:
    blocks = [''] * r
    for i, char in enumerate(ciphertext):
        blocks[i % r] += char
    return blocks


def decrypt_vigenere(ciphertext: str, key: str) -> str:
    decrypted_text = []
    key_len = len(key)

    for i, char_y in enumerate(ciphertext):
        y = char_to_num(char_y)
        k = char_to_num(key[i % key_len])
        x = (y - k) % M
        decrypted_text.append(num_to_char(x))

    return "".join(decrypted_text)


def find_key_length(ciphertext: str, max_r: int) -> int:
    ic_averages = {}

    for r in range(2, max_r + 1):
        blocks = split_ciphertext(ciphertext, r)
        ic_sum = sum(index_of_coincidence(block) for block in blocks)
        ic_avg = ic_sum / r
        ic_averages[r] = ic_avg

    threshold = (MI_RUSSIAN + I0_UNIFORM) / 2

    candidates = {r: ic for r, ic in ic_averages.items() if ic > threshold}

    if candidates:
        best_r = min(candidates, key=lambda r: abs(candidates[r] - MI_RUSSIAN))
    else:
        best_r = max(ic_averages, key=ic_averages.get)

    print(f"Аналіз індексу відповідності блоків до r={max_r}:")
    print(
        f"Найкращий кандидат r (за IC_avg): {best_r} (IC_avg: {ic_averages[best_r]:.5f})")

    return best_r


def find_caesar_key(ciphertext: str,  key_length: int) -> int:
    key = ''
    blocks = split_ciphertext(ciphertext, key_length)

    for block in blocks:
        if not blocks:
            key += ALPHABET[0]
            continue

        freq = Counter(block)
        sorted_letters: list = [ltr for ltr, _ in freq.most_common(3)]
        cands: list = []

        for most_freq_letter in ["о", "е", "а", "и"]:
            freq_letter_indx = char_to_num(most_freq_letter)

            for block_letter in sorted_letters:
                block_letter_idx = char_to_num(block_letter)
                key_letter_indx = (block_letter_idx - freq_letter_indx) % M
                cands.append(num_to_char(key_letter_indx))
    
        key_char = Counter(cands).most_common(1)[0][0]
        key += key_char

    return key


def recover_key_and_decrypt(ciphertext: str, r: int):
    key = find_caesar_key(ciphertext, r)
    plaintext_result = decrypt_vigenere(ciphertext, key)

    return key, plaintext_result


def main_cryptoanalysis():
    print("--- ЗАВДАННЯ 3: КРИПТОАНАЛІЗ ШИФРУ ВІЖЕНЕРА (Варіант 1) ---")

    ciphertext = read_text_from_file(CIPHER_FILE)
    r = find_key_length(ciphertext, MAX_KEY_LENGTH)
    print(f"\n[КРОК 1] Використовуваний період ключа (r): {r}")

    key, plaintext_result = recover_key_and_decrypt(ciphertext, r)

    print(
        f"\n[КРОК 2] Знайдений ключ (на основі статистики): {key.upper()} (Довжина {len(key)})")

    print("\n[КРОК 3] Розшифрований текст (Фрагмент):")
    print("-" * 50)
    print(plaintext_result[:400] + "...")
    print("-" * 50)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    decrypted_file = OUT_DIR / "decrypted_v1.txt"
    decrypted_file.write_text(plaintext_result, encoding='utf-8')
    print(
        f"\nПовний розшифрований текст (за ключем '{key.upper()}') збережено у файл: {decrypted_file.resolve()}")


if __name__ == "__main__":
    main_cryptoanalysis()
