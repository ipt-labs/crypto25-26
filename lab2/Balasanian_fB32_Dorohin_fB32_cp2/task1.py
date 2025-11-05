import pandas as pd
import matplotlib.pyplot as plt

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def prepare_text(text):
    text = text.lower()
    return "".join([c for c in text if c in ALPHABET])

def sanitize_key(key):
    clean = "".join([c for c in key.lower() if c in ALPHABET])
    if clean != key:
        print(f"Увага: ключ '{key}' був очищений до '{clean}' (видалені недопустимі символи).")
    return clean

def vigenere_encrypt(text, key):
    key = sanitize_key(key)
    if len(key) == 0:
        raise ValueError("Ключ пустий після очищення — виберіть інший ключ.")
    n = len(ALPHABET)
    key_indices = [ALPHABET.index(k) for k in key]
    cipher = []
    for i, c in enumerate(text):
        ci = (ALPHABET.index(c) + key_indices[i % len(key)]) % n
        cipher.append(ALPHABET[ci])
    return "".join(cipher)

def index_of_coincidence(text):
    N = len(text)
    freqs = [text.count(c) for c in ALPHABET]
    return sum(f*(f-1) for f in freqs) / (N*(N-1)) if N > 1 else 0

with open("text1.txt", "r", encoding="utf-8") as f:
    raw = f.read()

text = prepare_text(raw)
print("Довжина підготовленого тексту:", len(text))

short_keys = ["но", "мир", "світ", "книга"]
long_keys = [ALPHABET[:L] for L in range(10, 21)]
keys = short_keys + long_keys


ic_plain = index_of_coincidence(text)
print(f"\nIC відкритого тексту: {ic_plain:.4f}\n")

results = []
results.append({"ключ": "відкритий текст", "індекс": ic_plain, "різниця з ориг.": "-"})

for key in keys:
    clean_key = sanitize_key(key)
    cipher = vigenere_encrypt(text, clean_key)
    ic_cipher = index_of_coincidence(cipher)
    diff = abs(ic_plain - ic_cipher)
    results.append({"ключ": clean_key, "індекс": ic_cipher, "різниця з ориг.": round(diff, 6)})
    print(f"Ключ: {clean_key:20s} | довжина: {len(clean_key):2d} | IC: {ic_cipher:.6f}")


df = pd.DataFrame(results)
print("\nТаблиця індексів відповідності:")
print(df)

plt.figure(figsize=(10,5))
plot_df = df[df["ключ"] != "відкритий текст"]
plt.bar(plot_df["ключ"], plot_df["індекс"], color="skyblue")
plt.axhline(ic_plain, color="green", linestyle="--", label="IC відкритого тексту")
plt.axhline(0.0569, color="red", linestyle="--", label="Теоретичне значення (≈0.0569)")
plt.xticks(rotation=45, ha="right")
plt.ylabel("Індекс відповідності")
plt.title("Індекси відповідності для різних ключів шифру Віженера")
plt.legend()
plt.tight_layout()
plt.show()
