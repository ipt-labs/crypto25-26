from collections import Counter
import os

alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
ALPHABET_SIZE = len(alphabet)

RUSSIAN_FREQUENCIES_10000 = [
    820, 159, 450, 170, 318, 791, 94, 165, 745, 121, 349, 440, 322, 670, 1097, 280,
    476, 547, 621, 262, 20, 86, 51, 144, 49, 30, 3, 189, 174, 37, 17, 201
]

def index_of_coincidence(text):
    n = len(text)
    if n <= 1:
        return 0
    counts = Counter(text)
    return sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))

def find_key_length(ciphertext, max_r=30):
    russian_ic = 0.0553
    best_r, best_ic_diff = 0, float('inf')

    print(f"{'Довжина ключа':<15} {'Середній IC':<15} {'Відхилення':<30}")
    print("-" * 60)

    for r in range(2, max_r + 1):
        blocks = [''.join(ciphertext[i::r]) for i in range(r)]
        avg_ic = sum(index_of_coincidence(block) for block in blocks) / r
        ic_diff = abs(avg_ic - russian_ic)
        print(f"{r:<15} {avg_ic:<15.4f} {ic_diff:<30.4f}")
        if ic_diff < best_ic_diff:
            best_ic_diff, best_r = ic_diff, r
    return best_r

def caesar_decrypt(char, shift, alphabet):
    if char not in alphabet:
        return char
    return alphabet[(alphabet.index(char) - shift) % ALPHABET_SIZE]

def chi_squared_test(block, shift):
    decrypted = [caesar_decrypt(c, shift, alphabet) for c in block]
    counts = Counter(decrypted)
    chi_sq = 0
    for i in range(ALPHABET_SIZE):
        expected = len(block) * (RUSSIAN_FREQUENCIES_10000[i] / 10000)
        observed = counts.get(alphabet[i], 0)
        if expected > 0:
            chi_sq += (observed - expected) ** 2 / expected
    return chi_sq

def break_vigenere_by_frequency(ciphertext, key_length):
    blocks = [''.join(ciphertext[i::key_length]) for i in range(key_length)]
    key_shifts = []

    print("\n--- Визначення ключа ---")
    for i, block in enumerate(blocks):
        best_shift, best_chi = 0, float('inf')
        for shift in range(ALPHABET_SIZE):
            chi = chi_squared_test(block, shift)
            if chi < best_chi:
                best_chi, best_shift = chi, shift
        key_shifts.append(best_shift)
        print(f"Блок {i+1}/{key_length}: shift = {best_shift} ({alphabet[best_shift]}), χ² = {best_chi:.2f}")

    key = ''.join(alphabet[s] for s in key_shifts)
    plaintext = [caesar_decrypt(c, key_shifts[i % key_length], alphabet) for i, c in enumerate(ciphertext)]
    return ''.join(plaintext), key

input_path = r"C:\Users\u1208\OneDrive\Робочий стіл\5 сем\lab2crypto\lab2\var4.txt"
output_path = os.path.join(os.path.dirname(input_path), "var4_decrypted.txt")

try:
    with open(input_path, 'r', encoding='utf-8') as f:
        ciphertext_raw = f.read()
except FileNotFoundError:
    print(f"Файл не знайдено: {input_path}")

ciphertext = ''.join(c for c in ciphertext_raw.lower() if c in alphabet)

if ciphertext:
    key_length = find_key_length(ciphertext)
    print(f"\n=== Знайдена довжина ключа: {key_length} ===")
    plaintext, key = break_vigenere_by_frequency(ciphertext, key_length)
    print(f"\n=== ЗНАЙДЕНИЙ КЛЮЧ: {key} ===")
    print("\nФрагмент тексту (перші 500 символів):\n")
    print(plaintext[:500])
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(plaintext)
    print(f"\n Розшифрований текст збережено у файл: {output_path}")
else:
    print("Помилка: Шифротекст порожній або без символів алфавіту.")
