import os
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)  # m = 32

def calculate_ioc(text):
    n = len(text)
    if n < 2:
        return 0.0

    counts = Counter(text)
    numerator = 0.0
    for char in ALPHABET:
        Nt = counts[char]
        numerator += Nt * (Nt - 1)

    denominator = n * (n - 1)
    ioc = numerator / denominator
    return ioc

def vigenere_encrypt(plaintext, key):
    ciphertext = []
    key_length = len(key) 
    key_indices = [ALPHABET.index(k) for k in key]

    for i, char in enumerate(plaintext):
        text_index = ALPHABET.index(char)
        key_index = key_indices[i % key_length]
        cipher_index = (text_index + key_index) % M
        ciphertext.append(ALPHABET[cipher_index])

    return "".join(ciphertext)

def calculate_ic_language(monogram_file_path):
    try:
        df = pd.read_excel(monogram_file_path)
        ic_language = (df['Ймовірність'] ** 2).sum()
        return ic_language
    except Exception:
        return None

TEXT_FILE = "text_lab2.txt"
GRAPH_FILE = "ioc_dependency_graph.png"
CIPHERTEXTS_OUTPUT_FILE = "all_ciphertexts.txt"

# Визначення ключів
meaningful_keys = [
    "он",                     # r=2
    "дом",                    # r=3
    "шкаф",                   # r=4
    "мосту",                  # r=5
    "хозяйкой",               # r=8
    "одинмолодойчел",         # r=14
    "вначалеиюлявчрезвы"      # r=18
]

# Перевірка, чи існує файл
if not os.path.exists(TEXT_FILE):
    print(f"ПОМИЛКА: Файл '{TEXT_FILE}' не знайдено.")
else:
    # Читання та очищення тексту про всяк випадок
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        plaintext = f.read()

    plaintext = plaintext.lower().replace("ё", "е")
    clean_plaintext = "".join(c for c in plaintext if c in ALPHABET)

    ioc_values_cipher = {} 
    # Обчислення I(Y) для ВТ
    ioc_plaintext = calculate_ioc(clean_plaintext)
    print(f"\nІндекс відповідності для відкритого тексту: {ioc_plaintext:.6f}")

    # файл для запису всіх ШТ
    with open(CIPHERTEXTS_OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        # Записуємо у файл відкритий текст для порівняння
        f_out.write("--- ВІДКРИТИЙ ТЕКСТ ---\n")
        f_out.write(clean_plaintext + "\n")

        for key in meaningful_keys:
            r = len(key)
            ciphertext = vigenere_encrypt(clean_plaintext, key)
            if ciphertext:
                # Обчислюємо індекс
                ioc_cipher = calculate_ioc(ciphertext)
                ioc_values_cipher[r] = ioc_cipher

                header = f"\n--- Шифротекст для ключа r={r}, Ключ = '{key}' ---"
                f_out.write(header + "\n")
                f_out.write(ciphertext + "\n")

                print(f"\n  r = {r:2}, Ключ = '{key}', I(Y) = {ioc_cipher:.6f}")
                print(f"   -> Шифротекст додано до файлу: {CIPHERTEXTS_OUTPUT_FILE}")

        print(f"Шифротексти збережено в одному файлі: {CIPHERTEXTS_OUTPUT_FILE}")

        # Побудова діаграми
        monogram_file = "monogram_no_spaces.xlsx"
        ioc_russian_ideal = calculate_ic_language(monogram_file)
        if ioc_russian_ideal is None: 
            ioc_russian_ideal = 0.0553 # значення з вікіпедії
        ioc_random_ideal = 1.0 / M

        plt.figure(figsize=(12, 7))

        lengths = list(ioc_values_cipher.keys())
        values = list(ioc_values_cipher.values())
        plt.plot(lengths, values, 'bo-',
                 label='I(Y) шифротексту')

        plt.axhline(y=ioc_plaintext, color='r', linestyle='--',
                    label=f'I(Y) відкритого тексту ({ioc_plaintext:.4f})')
        plt.axhline(y=ioc_russian_ideal, color='orange', linestyle=':',
                    label=f'Теоретичний I(Y) рос. мови ({ioc_russian_ideal:.4f})')
        plt.axhline(y=ioc_random_ideal, color='g', linestyle='--',
                    label=f'Теоретичний I(Y) випадк. тексту (1/32 = {ioc_random_ideal:.4f})')

        plt.title(
            'Залежність індексу відповідності (I) від довжини ключа (r)', fontsize=14)
        plt.xlabel('Довжина ключа (r)', fontsize=12)
        plt.ylabel('Індекс відповідності (I)', fontsize=12)
        plt.xticks(lengths)
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)

        plt.savefig(GRAPH_FILE)
        print(f"\nДіаграму збережено у файл: {GRAPH_FILE}")