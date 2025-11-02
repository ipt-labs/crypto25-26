import re
from collections import Counter
import matplotlib.pyplot as plt

ALPHABET = list("абвгдежзийклмнопрстуфхцчшщъыьэюя")  # 32 літери, без "ё"
M = len(ALPHABET)
IDEAL_IC = 0.0553
A = set(ALPHABET)
pos = {c: i for i, c in enumerate(ALPHABET)}

R_FREQ = {
    'а':0.0801,'б':0.0159,'в':0.0454,'г':0.0170,'д':0.0298,'е':0.0845,
    'ж':0.0094,'з':0.0165,'и':0.0735,'й':0.0121,'к':0.0349,'л':0.0440,
    'м':0.0321,'н':0.0670,'о':0.1097,'п':0.0281,'р':0.0473,'с':0.0547,
    'т':0.0626,'у':0.0262,'ф':0.0026,'х':0.0097,'ц':0.0048,'ч':0.0144,
    'ш':0.0073,'щ':0.0036,'ъ':0.0004,'ы':0.0190,'ь':0.0174,'э':0.0032,
    'ю':0.0064,'я':0.0201
}

def clean_text(text: str) -> str:
    text = text.lower().replace("ё", "е")
    return ''.join(ch for ch in text if ch in A)

def index_of_coincidence(text: str) -> float:
    n = len(text)
    if n < 2: return 0.0
    freq = Counter(text)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

def get_blocks(text: str, r: int):
    return [text[i::r] for i in range(r)]

def avg_ic_for_r(text: str, r: int) -> float:
    subs = get_blocks(text, r)
    ics = [index_of_coincidence(s) for s in subs if len(s) > 1]
    return sum(ics) / len(ics) if ics else 0.0

def guess_key_length(text: str, r_max=30):
    results = {r: avg_ic_for_r(text, r) for r in range(1, r_max+1)}
    best_r = max(results, key=lambda k: results[k])
    return best_r, results

def chi_squared(text: str) -> float:
    n = len(text)
    if n == 0:
        return float('inf')
    freq = Counter(text)
    chi = 0.0
    for ch in ALPHABET:
        exp = n * R_FREQ.get(ch, 0)
        obs = freq.get(ch, 0)
        if exp > 0:
            chi += (obs - exp) ** 2 / exp
    return chi

def guess_key_by_mostfreq(cipher: str, r: int, candidates=('о','е')) -> str:

    key = []
    print("\n--- Детальний аналіз блоків ---\n")
    for i in range(r):
        block = cipher[i::r]
        if not block:
            key.append('а')
            continue
        most = Counter(block).most_common(1)[0][0]

        best_common, best_shift, best_chi, best_keych = None, None, float('inf'), None

        for common in candidates:
            shift = (pos[most] - pos[common]) % M
            dec_block = ''.join(ALPHABET[(pos[c]-shift) % M] for c in block)
            chi = chi_squared(dec_block)
            if chi < best_chi:
                best_chi = chi
                best_common = common
                best_shift = shift
                best_keych = ALPHABET[shift]

        print(f"Блок {i+1:2d}: найчастіша літера '{most}', "
              f"припущена базова '{best_common}', "
              f"зсув = {best_shift:2d}, "
              f"літера ключа = '{best_keych}' (χ²={best_chi:.4f})")

        key.append(best_keych)
    return ''.join(key)

def shorten_key_period(key: str) -> str:
    n = len(key)
    for L in range(1, n//2 + 1):
        if n % L == 0 and key[:L] * (n//L) == key:
            return key[:L]
    return key

def decrypt(ciphertext: str, key: str) -> str:
    kidx = [pos[k] for k in key]
    out = []
    for i, c in enumerate(ciphertext):
        out.append(ALPHABET[(pos[c] - kidx[i % len(kidx)]) % M])
    return ''.join(out)

def main():
    filename = "variant12.txt"
    with open(filename, "r", encoding="utf-8") as f:
        raw = f.read()
    text = clean_text(raw)
    if not text:
        print("Порожній або некоректний шифртекст.")
        return

    # довжина ключа
    best_r, ic_values = guess_key_length(text)
    print(f"Ймовірна довжина ключа: {best_r}\n")
    print(" r |   I(r)")
    print("------------")
    for r, ic in ic_values.items():
        print(f"{r:2d} | {ic:.4f}")
    print("------------")

    # графік
    plt.figure(figsize=(10,5))
    plt.bar(list(ic_values.keys()), list(ic_values.values()), label="I(r)")
    plt.axhline(IDEAL_IC, color="red", linestyle="--", label=f"IC теор = {IDEAL_IC:.4f}")
    plt.xlabel("Довжина ключа r "); plt.ylabel("Індекс відповідності I(r)")
    plt.title("Залежність індексу відповідності від довжини ключа")
    plt.legend(); plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout(); plt.show()

    # ключ
    key_raw = guess_key_by_mostfreq(text, best_r)
    key = shorten_key_period(key_raw)
    print("\nЙмовірний ключ (до скорочення):", key_raw)
    if key != key_raw:
        print("Скорочено до базового періоду:", key)
    else:
        print("Внутрішнього повтору немає.")

    # розшифрування
    decrypted = decrypt(text, key)
    print("\nРозшифрований текст:\n")
    print(decrypted)

    with open("variant12_decrypt.txt", "w", encoding="utf-8") as f:
        f.write(decrypted)
    print("\nРозшифровано. Результат збережено у decrypt_variant12.txt")

if __name__ == "__main__":
    main()
