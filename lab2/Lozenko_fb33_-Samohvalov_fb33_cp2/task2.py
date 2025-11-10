import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

# --- 1. Налаштування ---
ABC = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ABC)
FREQS = [
    0.0800, 0.0159, 0.0454, 0.0170, 0.0298, 0.0848, 0.0094, 0.0165, 0.0734, 0.0121,
    0.0349, 0.0434, 0.0321, 0.0670, 0.1098, 0.0281, 0.0473, 0.0547, 0.0632, 0.0262,
    0.0027, 0.0097, 0.0048, 0.0144, 0.0073, 0.0036, 0.0004, 0.0190, 0.0174, 0.0032,
    0.0064, 0.0201
]
IC_LANG = 0.0563
IC_RAND = 1 / M
MAX_R = 30 # Максимальна довжина ключа для перевірки

# --- 2. Функції ---
def clean(raw_data):
    """Очищує текст."""
    return "".join(c for c in raw_data.lower().replace('ё', 'е') if c in ABC)

def calc_ic(txt):
    """Рахує індекс відповідності."""
    N = len(txt)
    return sum(c*(c-1) for c in Counter(txt).values()) / (N*(N-1)) if N > 1 else 0

def get_cols(txt, r):
    """Розбиває текст на r стовпців."""
    cols = [''] * r
    for i, c in enumerate(txt):
        cols[i % r] += c
    return cols

def find_shift(col):
    """Знаходить зсув стовпця (атака X^2)."""
    min_chi, best_s = float('inf'), 0
    N = len(col)
    if N == 0: return 0
    for s in range(M):
        chi_sq = 0
        obs = [0] * M
        for c in col:
            obs[(ABC.find(c) - s) % M] += 1
        for i in range(M):
            exp = N * FREQS[i]
            if exp > 0:
                chi_sq += ((obs[i] - exp) ** 2) / exp
        if chi_sq < min_chi:
            min_chi, best_s = chi_sq, s
    return best_s

def decrypt(txt, key):
    """Дешифрує текст."""
    key_idx = [ABC.find(k) for k in key]
    r = len(key)
    return "".join(ABC[(ABC.find(c) - key_idx[i % r] + M) % M] for i, c in enumerate(txt))

# --- 3. Основний процес ---
try:
    with open("cipher.txt", "r", encoding="utf-8") as f:
        ciphertext = clean(f.read())
    print(f"Очищено {len(ciphertext)} символів.")
except FileNotFoundError:
    print("ПОМИЛКА: Файл 'cipher.txt' не знайдено.")
    exit()

# 1. Пошук довжини ключа
r_range = range(1, MAX_R + 1)
ic_vals = []
print("r\tAvg IC")
for r in r_range:
    cols = get_cols(ciphertext, r)
    avg_ic = sum(calc_ic(c) for c in cols) / r
    ic_vals.append(avg_ic)
    print(f"{r}\t{avg_ic:.5f}")

# 2. Визначення ключа (автоматично)
# Шукаємо піки вище середнього між випадковим і мовним IC
threshold = IC_RAND + (IC_LANG - IC_RAND) * 0.4
likely_r = [r for r, ic in zip(r_range, ic_vals) if ic > threshold and r > 1]
best_r = min(likely_r) if likely_r else np.argmax(ic_vals[1:]) + 2

print(f"\nЙмовірні довжини: {likely_r}")
print(f"Обрана довжина ключа: {best_r}")

# 3. Злам ключа
key_chars = [ABC[find_shift(col)] for col in get_cols(ciphertext, best_r)]
key = "".join(key_chars)
print(f"Знайдений ключ: '{key}'")

# 4. Дешифрування
plaintext = decrypt(ciphertext, key)
print("\n--- Розшифрований текст (початок) ---")
print(plaintext[:500] + "...")

with open("decrypted_message_short.txt", "w", encoding="utf-8") as f:
    f.write(f"Key: {key}\nLength: {best_r}\n\n{plaintext}")
print("\nТекст збережено у 'decrypted_message_short.txt'")

# 5. Графік
plt.figure(figsize=(12, 6))
plt.bar(r_range, ic_vals, color='cyan', label='Середній IC для r')
plt.axhline(y=IC_LANG, color='r', ls='--', label=f'IC Мови ({IC_LANG:.4f})')
plt.axhline(y=IC_RAND, color='g', ls=':', label=f'IC Випадковий ({IC_RAND:.4f})')
plt.xlabel("Довжина ключа (r)")
plt.ylabel("Середній індекс відповідності")
plt.title("Аналіз довжини ключа")
plt.xticks(r_range)
plt.legend()
plt.tight_layout()
plt.savefig("ic_analysis_plot.png")
print("Графік 'ic_analysis_plot.png' збережено.")
plt.show()