import re
from collections import Counter
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np

with open("warandpeace2.txt", "r", encoding="utf-8") as f:
    text = f.read().lower()

text = text.replace("ё", "е")
text = re.sub(r"[^абвгдежзийклмнопрстуфхцчшщъыьэюя]", "", text)

with open("prepared_text.txt", "w", encoding="utf-8") as f:
    f.write(text)
print("Відформатований текст збережено у prepared_text.txt")

alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
m = len(alphabet)

def clean_key(key):
    return "".join([ch for ch in key if ch in alphabet])

def vigenere_encrypt(plaintext, key):
    key = clean_key(key)
    alpha_index = {ch: i for i, ch in enumerate(alphabet)}
    index_alpha = {i: ch for i, ch in enumerate(alphabet)}
    ciphertext = ""
    for i, ch in enumerate(plaintext):
        k = alpha_index[key[i % len(key)]]
        c = (alpha_index[ch] + k) % m
        ciphertext += index_alpha[c]
    return ciphertext

def index_of_coincidence(text):
    n = len(text)
    freq = Counter(text)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

keys = [
    "ля", "два", "клас", "война", "классикака", "длинныйключ",
    "дружбаняключ", "геройскийтест", "литературочкаа", "приключенскийпр",
    "историческийклас", "сражениеилипобеда", "любовьсчастьенавек",
    "ехсудьбаприключение", "романтикаволяпревише"
]

keys = [clean_key(k) for k in keys]

with open("all_ciphers.txt", "w", encoding="utf-8") as f:
    for key in keys:
        cipher = vigenere_encrypt(text, key)
        f.write(f"=== Ключ: {key} ===\n")
        f.write(cipher + "\n\n")
print("Всі шифртексти збережено у all_ciphers.txt")

indices = {}
indices["Відкритий текст"] = index_of_coincidence(text)
for key in keys:
    cipher = vigenere_encrypt(text, key)
    indices[key] = index_of_coincidence(cipher)

table_data = [[key, f"{I:.5f}"] for key, I in indices.items()]
table_text = tabulate(table_data, headers=["Ключ", "I"], tablefmt="rounded_grid")

keys_for_plot = list(indices.keys())
values_for_plot = list(indices.values())
n = len(values_for_plot)

plt.figure(figsize=(14, 7))
colors = plt.cm.Purples(np.linspace(0.4, 0.8, n))
bars = plt.bar(range(n), values_for_plot, color=colors)
plt.xticks(range(n), keys_for_plot, rotation=45, ha='right', fontsize=10)
plt.ylabel("Індекс відповідності (I)", fontsize=12)
plt.title("Індекси відповідності для відкритого тексту та шифртекстів", fontsize=14)
y_min = min(values_for_plot)
y_max = max(values_for_plot)
plt.yticks(np.arange(round(y_min, 3), round(y_max + 0.005, 3), 0.005))
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar, val in zip(bars, values_for_plot):
    plt.text(bar.get_x() + bar.get_width() / 2, val + 0.0005, f"{val:.5f}", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig("indices_plot.png", dpi=300)
plt.close()
print("Діаграма індексів відповідності збережена у indices_plot.png")

with open("indices_table.txt", "w", encoding="utf-8") as f:
    f.write(table_text)
print("Таблиця індексів відповідності збережена у indices_table.txt")
