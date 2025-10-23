# -*- coding: utf-8 -*-
# lab2.py — Віженер: шифрування r=2..20, збереження файлів, IoC-таблиця

from collections import Counter
from pathlib import Path
import csv

# ===== Налаштування шляхів =====
BASE_DIR = Path(__file__).resolve().parent
OPEN_PATH = BASE_DIR / "textlab2.txt"
CSV_PATH = BASE_DIR / "ioc_results.csv"
KEYS_PATH = BASE_DIR / "keys_used.txt"

# ===== Російський алфавіт (без 'ё'), m = 32 =====
ALPH = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPH)
A2I = {ch: i for i, ch in enumerate(ALPH)}
I2A = {i: ch for i, ch in enumerate(ALPH)}

def normalize_text(s: str) -> str:
    """Нижній регістр, 'ё'->'е', лишаємо тільки наші букви."""
    s = s.lower().replace("ё", "е")
    return "".join(ch for ch in s if ch in A2I)

def vigenere_encrypt(clean_text: str, key: str) -> str:
    """Шифр Віженера (тільки по літерах ALPH)."""
    k = normalize_text(key)
    if not k:
        raise ValueError("Порожній ключ після нормалізації. Використайте російські букви без 'ё'.")
    out = []
    for i, ch in enumerate(clean_text):
        x = A2I[ch]
        y = (x + A2I[k[i % len(k)]]) % M
        out.append(I2A[y])
    return "".join(out)

def index_of_coincidence(clean_text: str) -> float:
    """IoC = sum(Nj(Nj-1)) / (n(n-1))"""
    n = len(clean_text)
    if n < 2:
        return 0.0
    cnt = Counter(clean_text)
    num = sum(v * (v - 1) for v in cnt.values())
    return num / (n * (n - 1))

# ===== 1) Зчитати й нормалізувати відкритий текст =====
if not OPEN_PATH.exists():
    raise FileNotFoundError(f"Не знайдено файл {OPEN_PATH}. Поклади сюди textlab2.txt")

raw = OPEN_PATH.read_text(encoding="utf-8", errors="ignore")
open_clean = normalize_text(raw)

# Якщо треба добити до ~2–3 КБ — повторимо вміст (не змінюючи розподілів)
while len(open_clean) < 2200:
    open_clean += open_clean

print(f"Довжина відкритого (очищеного) тексту: {len(open_clean)} символів (m={M})")
print(f"I_open = {index_of_coincidence(open_clean):.5f}\n")

# ===== 2) ключі (без 'ё') =====
seed_words = [
    "да", "мир", "ключ", "текст", "пример", "поездка", "алгоритм",
    "универсал", "переменная", "эксперимент", "безопасность",
    "распознавание", "инфраструктура", "маскировка", "статистика",
    "последователь", "криптоанализ", "перекодировка", "криптосистема",
    "методологически"
]
# Примітка: ключ формується як repeat/trim до точної довжини r

def make_key(target_len: int) -> str:
    base = seed_words[min(target_len-1, len(seed_words)-1)]
    base = normalize_text(base)
    if len(base) == 0:
        base = "ключ"
    # повторити і обрізати
    rep = (target_len + len(base) - 1) // len(base)
    return (base * rep)[:target_len]

# ===== 3) Шифруємо r=2..20, рахуємо IoC, зберігаємо файли =====
rows = []
used_keys_lines = ["Список ключів (фактична довжина r):"]
print(f"{'r':<3} {'ключ':<22} {'IoC':>8}   файл")
print("-"*50)

for r in range(2, 21):
    key = make_key(r)  # ключ точно довжини r
    cipher = vigenere_encrypt(open_clean, key)
    ioc = index_of_coincidence(cipher)

    out_path = BASE_DIR / f"encrypted_{r}.txt"
    out_path.write_text(cipher, encoding="utf-8")

    print(f"{r:<3} {key:<22} {ioc:>8.5f}   {out_path.name}")
    rows.append(["cipher", r, key, ioc, out_path.name])
    used_keys_lines.append(f"r={r:>2}: {key}")

# додамо також відкритий текст до таблиці
rows.insert(0, ["open_text", "-", "-", index_of_coincidence(open_clean), "—"])

# === Графік IoC vs довжина ключа r ===
import matplotlib.pyplot as plt

ioc_open = index_of_coincidence(open_clean)
rs = list(range(2, 21))
iocs = []
for r in rs:
    key = make_key(r)
    c = vigenere_encrypt(open_clean, key)
    iocs.append(index_of_coincidence(c))

plt.figure()
plt.plot(rs, iocs, marker='o')              # IoC шифртекстів
plt.axhline(ioc_open, linestyle='--')       # рівень відкритого тексту
plt.title('Індекс відповідності (IoC) залежно від довжини ключа r')
plt.xlabel('Довжина ключа r')
plt.ylabel('IoC')
plt.xticks(rs)
plt.grid(True, linestyle=':', linewidth=0.5)
plt.tight_layout()
plt.savefig(BASE_DIR / 'ioc_plot.png', dpi=200)

print(f" - графік: ioc_plot.png")

# ===== 4) Зберегти таблицю IoC у CSV =====
with CSV_PATH.open("w", newline="", encoding="cp1251") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["type", "r", "key", "IoC", "file"])
    for row in rows:
        w.writerow(row)

# ===== 5) Зберегти список використаних ключів =====
KEYS_PATH.write_text("\n".join(used_keys_lines), encoding="utf-8")

print("\nЗбережено:")
print(f" - шифртексти: encrypted_2.txt … encrypted_20.txt")
print(f" - таблиця IoC: {CSV_PATH.name}")
print(f" - ключі: {KEYS_PATH.name}")