import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

def clean_text(text):
    text = text.lower().replace("ё", "е").replace("ъ", "ь")
    return re.sub(r'[^а-я]', '', text)

# шифр Віженера
def vigenere_encrypt(text, key, alphabet):
    m = len(alphabet)
    key_idx = [alphabet.index(k) for k in key]
    return ''.join(alphabet[(alphabet.index(ch) + key_idx[i % len(key)]) % m]
                   for i, ch in enumerate(text))

# індекс відповідності
def index_of_coincidence(text):
    n = len(text)
    freq = Counter(text)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) if n > 1 else 0

alphabet = [chr(c) for c in range(ord('а'), ord('я') + 1)]

with open("duymovochka.txt", "r", encoding="utf-8") as f:
    text = clean_text(f.read())

ic_open = index_of_coincidence(text)

# ключі
keys = {
    2:  "он",
    3:  "шум",
    4:  "звук",
    5:  "огонь",
    6:  "судьба",
    7:  "счастье",
    8:  "нежность",
    9:  "вдохновенье",
    10: "путешествие",
    11: "воспоминанье",
    12: "волшебствоночь",
    13: "звездынаднами",
    14: "пепелвремени",
    15: "тихаямелодия",
    16: "сияниенебесное",
    17: "отражениедуши",
    18: "зачарованноеморе",
    19: "прикосновениесна",
    20: "наперекорвремени"
}

# обчислення IC
labels = ["Відкритий"] + [f"r={r}" for r in keys.keys()]
ic_values = [ic_open]
saved_files = []

print(f"\nІндекс відповідності відкритого тексту: {ic_open:.5f}\n")
print("  r |            Ключ             |  IC (шифртексту)")
print("-----------------------------------------------------")

for r, key in keys.items():
    cipher = vigenere_encrypt(text, key, alphabet)
    ic = index_of_coincidence(cipher)
    ic_values.append(ic)
    print(f"{r:3d} | {key:<27} | {ic:.5f}")
    
    filename = f"cipher_r{r}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cipher)
    saved_files.append(filename)

print("-----------------------------------------------------")
print("\nЗбережені файли шифртекстів:")
print("-----------------------------")
for file in saved_files:
    print(file)

# графік
plt.figure(figsize=(22, 8))
colors = cm.cool(np.linspace(0.1, 0.9, len(labels)))
bars = plt.bar(range(len(labels)), ic_values, color=colors, edgecolor="#1f1f1f", linewidth=0.6)

bars[0].set_color("#2ecc71")
bars[0].set_edgecolor("#145a32")

plt.gca().set_facecolor("#f8fafb")
plt.title("Індекс відповідності для відкритого тексту та шифртекстів (шифр Віженера)",
          fontsize=14, pad=20, fontweight='bold')
plt.xlabel("Тип тексту / довжина ключа r", fontsize=12, labelpad=15)
plt.ylabel("Індекс відповідності (IC)", fontsize=12, labelpad=15)
plt.grid(axis='y', linestyle='--', alpha=0.6)

plt.xticks(range(len(labels)), labels, rotation=45, ha='center', fontsize=10)

for i, bar in enumerate(bars):
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.001, f"{yval:.05f}",
             ha='center', va='bottom', fontsize=9, rotation=90, color="#2c3e50")

plt.subplots_adjust(left=0.09, bottom=0.25, right=0.98, top=0.88)
plt.show()
