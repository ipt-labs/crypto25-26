import re
from collections import Counter
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np

# === Зчитування та очищення тексту ===
with open("text.txt", "r", encoding="utf-8") as src:
    content = src.read().lower()

# Нормалізація тексту
content = content.replace("ё", "е")
filtered_text = re.sub(r"[^а-я]", "", content)

# Збереження результату
with open("prepared_text.txt", "w", encoding="utf-8") as out:
    out.write(filtered_text)
print("✅ Очищений текст записано у prepared_text.txt")

# === Алфавіт ===
letters = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
n_letters = len(letters)

# === Функція очищення ключа ===
def normalize_key(key_phrase):
    return "".join(ch for ch in key_phrase if ch in letters)

# === Функція шифрування Віженера ===
def cipher_vigenere(data, key):
    key = normalize_key(key)
    char_to_num = {ch: i for i, ch in enumerate(letters)}
    num_to_char = {i: ch for i, ch in enumerate(letters)}

    encoded = []
    for i, sym in enumerate(data):
        key_shift = char_to_num[key[i % len(key)]]
        encoded_char = num_to_char[(char_to_num[sym] + key_shift) % n_letters]
        encoded.append(encoded_char)
    return "".join(encoded)

# === Індекс відповідності ===
def coincidence_ratio(sequence):
    n = len(sequence)
    freq = Counter(sequence)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

# === Набір ключів ===
key_variants = [ "да", "рот",
    "луна", "вода", "мечта", "звезда", "солнцесвет", "сказочныйключ",
    "вечерниеслова", "тайнаглубины", "мелодияветра", "небесныйпуть",
    "красотаночи", "поэзиявечности", "волшебныймирок",
    "искреннеесердце", "бесконечноелето"
]
key_variants = [normalize_key(k) for k in key_variants]

# === Генерація шифртекстів ===
print("🔐 Шифруємо тексти з різними ключами...")

results = {"Відкритий текст": coincidence_ratio(filtered_text)}

with open("all_ciphers.txt", "w", encoding="utf-8") as out:
    for key in key_variants:
        encrypted_text = cipher_vigenere(filtered_text, key)
        out.write(f"=== Ключ: {key} ===\n{encrypted_text}\n\n")
        results[key] = coincidence_ratio(encrypted_text)

print("✅ Усі шифртексти збережено у all_ciphers.txt")

# === Таблиця індексів відповідності ===
table_rows = [[k, f"{v:.5f}"] for k, v in results.items()]
formatted = tabulate(table_rows, headers=["Ключ", "Індекс відповідності"], tablefmt="rounded_grid")

with open("indices_table.txt", "w", encoding="utf-8") as f:
    f.write(formatted)
print("✅ Таблиця індексів відповідності збережена у indices_table.txt")

# === Побудова діаграми ===
labels = list(results.keys())
values = list(results.values())

plt.figure(figsize=(14, 7))
colors = plt.cm.plasma(np.linspace(0.3, 0.8, len(values)))
bars = plt.bar(range(len(values)), values, color=colors)

plt.xticks(range(len(values)), labels, rotation=45, ha='right', fontsize=10)
plt.ylabel("Індекс відповідності (I)", fontsize=12)
plt.title("Порівняння індексів відповідності для різних ключів", fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Підписи значень
for bar, val in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width() / 2, val + 0.0005, f"{val:.5f}", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig("indices_plot.png", dpi=300)
plt.close()

print("✅ Діаграма індексів відповідності збережена у indices_plot.png")
