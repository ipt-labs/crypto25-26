import collections
import re

FILENAME = '02.txt'
TOP_N = 5

alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"
allowed_chars = set(alphabet)
m = len(alphabet)

bigram_counts = collections.Counter()
print(f"--- Аналіз ({m} букв, 'ё' -> 'е') ---")

try:
    with open(FILENAME, 'r', encoding='utf-8') as f:
        text = f.read()
    clean_text = "".join(filter(lambda char: char in allowed_chars, text.lower()))
    print(f"Файл {FILENAME} завантажений. Всього символів для аналізу: {len(clean_text)}")
    for i in range(0, len(clean_text) - 1, 2):
        bigram = clean_text[i:i+2]
        if len(bigram) == 2:
            bigram_counts[bigram] += 1
    print(f"\n--- {TOP_N} найбільш частих біграм ---")
    top_bigrams = bigram_counts.most_common(TOP_N)
    for bigram, count in top_bigrams:
        print(f"'{bigram}': {count} раз")
    print("\n" + "-"*30)
    print("Список біграм:")
    print("-" * 30)
    bigram_list = [bg for bg, count in top_bigrams]
    print(f"ciphertext_top_N = {bigram_list}")
    print("-" * 30)
except FileNotFoundError:
    print(f"Помилка: Файл '{FILENAME}' не знайдений.")
except Exception as e:
    print(f"Помилка: {e}")