import matplotlib.pyplot as plt
from collections import Counter
import os


ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
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
    if denominator == 0:
        return 0.0

    ioc = numerator / denominator
    return ioc


def vigenere_encrypt(plaintext, key):

    ciphertext = []
    key_length = len(key)

    try:
        key_indices = [ALPHABET.index(k) for k in key]
    except ValueError as e:
        print(
            f"Літера в ключі '{e.args[0][0]}' не знайдена в алфавіті.")
        return None

    for i, char in enumerate(plaintext):
        try:
            text_index = ALPHABET.index(char)
        except ValueError:
            continue

        key_index = key_indices[i % key_length]
        cipher_index = (text_index + key_index) % M
        ciphertext.append(ALPHABET[cipher_index])

    return "".join(ciphertext)


TEXT_FILE = "text_lab2.txt"
GRAPH_FILE = "ioc_dependency_graph.png"
CIPHERTEXTS_OUTPUT_FILE = "all_ciphertexts.txt"

# Визначення ключів
meaningful_keys = [
    "он",                     # r=2
    "дом",                    # r=3
    "шкаф",                   # r=4
    "мосту",                  # r=5
    "хозяйкой",               # r=9
    "одинмолодойчел",         # r=14
    "вначалеиюлявчрезвы"      # r=19
]

# Перевірка, чи існує файл
if not os.path.exists(TEXT_FILE):
    print(f"ПОМИЛКА: Файл '{TEXT_FILE}' не знайдено.")
else:
    # 2. Читання та очищення тексту про всяк випадок
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        plaintext = f.read()

    plaintext = plaintext.lower().replace("ё", "е")
    clean_plaintext = "".join(c for c in plaintext if c in ALPHABET)

    if len(clean_plaintext) == 0:
        print(
            f"ПОМИЛКА: Очищений текст у файлі '{TEXT_FILE}' порожній")
    else:
        print(
            f"Текст '{TEXT_FILE}' завантажено. Довжина очищеного тексту: {len(clean_plaintext)} символів.")

        ioc_values_cipher = {}

        # 3. Обчислення I(Y) для ВТ
        ioc_plaintext = calculate_ioc(clean_plaintext)
        print(
            f"\nІндекс відповідності для відкритого тексту: {ioc_plaintext:.6f}")

        # 4. файл для запису всіх ШТ
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

                    print(
                        f"\n  r = {r:2}, Ключ = '{key}', I(Y) = {ioc_cipher:.6f}")
                    print(
                        f"    -> Шифротекст додано до файлу: {CIPHERTEXTS_OUTPUT_FILE}")

        print(
            f"Шифротексти збережено в одному файлі: {CIPHERTEXTS_OUTPUT_FILE}")

        # 5. Побудова діаграми
        ioc_russian_ideal = 0.0529
        ioc_random_ideal = 1.0 / M

        plt.figure(figsize=(12, 7))

        lengths = list(ioc_values_cipher.keys())
        values = list(ioc_values_cipher.values())
        plt.plot(lengths, values, 'bo-',
                 label='I(Y) шифротексту')

        plt.axhline(y=ioc_plaintext, color='r', linestyle='--',
                    label=f'I(Y) відкритого тексту ({ioc_plaintext:.4f})')
        plt.axhline(y=ioc_russian_ideal, color='orange', linestyle=':',
                    label=f'Теоретичний I(Y) рос. мови ({ioc_russian_ideal})')
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
