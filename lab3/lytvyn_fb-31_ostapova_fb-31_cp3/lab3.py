import re
from collections import Counter
from itertools import permutations
from math import gcd

def extended_gcd(a: int, b: int):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b != 0:
        q = a // b
        a, b = b, a - q * b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0

def modular_inverse(a: int, n: int):
    a %= n
    g, x, _ = extended_gcd(a, n)
    if g != 1:
        return None
    return x % n

def solve_linear_congruence(A: int, B: int, N: int):
    A %= N
    B %= N
    g, x, _ = extended_gcd(A, N)
    if B % g != 0:
        return []
    A1, B1, N1 = A // g, B // g, N // g
    invA1 = modular_inverse(A1, N1)
    x0 = (invA1 * B1) % N1
    return [(x0 + k * N1) % N for k in range(g)]

alphabet = "абвгдежзийклмнопрстуфхцчшщьыэюя"
m = len(alphabet)
mod = m * m
A2I = {ch: i for i, ch in enumerate(alphabet)}
I2A = {i: ch for ch, i in A2I.items()}

top_ru_bi = ["ст", "но", "то", "на", "ен"]
log_lines = []

def log(msg: str):
    log_lines.append(msg)

def clean_text(text: str) -> str:
    text = text.lower().replace("ё", "е").replace("ъ", "ь")
    text = re.sub(f"[^{alphabet}]", "", text)
    if len(text) % 2 == 1:
        text = text[:-1]
    return text

def bigram_to_int(bg: str) -> int:
    return A2I[bg[0]] * m + A2I[bg[1]]

def int_to_bigram(x: int) -> str:
    return I2A[(x // m) % m] + I2A[x % m]

def bi_nonoverlap(s: str):
    return [s[i:i+2] for i in range(0, len(s), 2)]

def bi_overlap(s: str):
    return [s[i:i+2] for i in range(len(s)-1)]

class TextStatistics:
    def __init__(self, text: str):
        self.text = text
        self.letter_freq = self._letter_freq()
        self.bigram_freq_overlap = self._bigram_freq(overlap=True)
        self.bigram_freq_non_overlap = self._bigram_freq(overlap=False)

    def _letter_freq(self):
        cnt = Counter(self.text)
        total = len(self.text)
        return {ch: cnt[ch]/total for ch in cnt}

    def _bigram_freq(self, overlap=True):
        if overlap:
            bigrams = bi_overlap(self.text)
        else:
            bigrams = bi_nonoverlap(self.text)
        cnt = Counter(bigrams)
        total = sum(cnt.values())
        return {bg: (cnt[bg], cnt[bg]/total) for bg in cnt}

def decrypt_affine(ciphertext: str, a: int, b: int) -> str | None:
    if gcd(a, m) != 1:
        return None
    inv = modular_inverse(a, mod)
    if inv is None:
        return None
    result = []
    for bg in bi_nonoverlap(ciphertext):
        y = bigram_to_int(bg)
        x = (inv * ((y - b) % mod)) % mod
        result.append(int_to_bigram(x))
    return "".join(result)

frequent_letters = {"о": 0.09, "е": 0.08, "а": 0.07}
rare_letters = {"ф": 0.01, "щ": 0.01, "ь": 0.02}
bad_overlap_bigrams = {"аь", "еь", "ыь", "оь", "яь", "юь", "ьь", "йй"}

def looks_like_ru(s: str) -> bool:
    if not s:
        return False
    n = len(s)
    for l, threshold in frequent_letters.items():
        if s.count(l)/n < threshold:
            return False
    for l, max_freq in rare_letters.items():
        if s.count(l)/n > max_freq:
            return False
    over = Counter(bi_overlap(s))
    bad_count = sum(over.get(bg, 0) for bg in bad_overlap_bigrams)
    if bad_count > 0:
        return False
    return True

def key_candidates(X1: int, X2: int, Y1: int, Y2: int):
    A = (X1 - X2) % mod
    B = (Y1 - Y2) % mod
    sols = solve_linear_congruence(A, B, mod)
    for a in sols:
        if gcd(a, m) != 1:
            continue
        b = (Y1 - a * X1) % mod
        yield a, b

def attack(cipher_text: str):
    stats = TextStatistics(cipher_text)
    top_shifr = sorted(stats.bigram_freq_non_overlap.items(), key=lambda x: -x[1][1])[:5]

    print("\nTop 5 ciphertext bigrams (count | frequency):")
    print("-------------------------------")
    print(f"{'Bigram':<6} | {'Count':<6} | {'Freq':<6}")
    print("-------------------------------")
    for bg, (count, freq) in top_shifr:
        print(f"{bg:<6} | {count:<6} | {freq:.4f}")
    print("-------------------------------")

    X_vals = [bigram_to_int(bg) for bg in top_ru_bi]
    Y_vals = [bigram_to_int(bg) for bg, _ in top_shifr]

    seen_keys = set()
    results = []

    print("\nKey search in progress...\n")

    for X1, X2 in permutations(X_vals, 2):
        for Y1, Y2 in permutations(Y_vals, 2):
            for a, b in key_candidates(X1, X2, Y1, Y2):
                if (a, b) in seen_keys:
                    continue
                seen_keys.add((a, b))
                pt = decrypt_affine(cipher_text, a, b)
                if pt and looks_like_ru(pt):
                    msg = f"PASS (a={a}, b={b})"
                    print(msg)
                    print("   " + pt[:300] + "...\n")
                    log(msg)
                    results.append((a, b, pt))
                else:
                    log(f"FAIL (a={a}, b={b})")

    print(f"\nChecked {len(seen_keys)} candidate keys.")
    return results

def main():
    input_file = "10.txt"
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
        return

    ct = clean_text(raw)
    print(f"Ciphertext length: {len(ct)} characters")

    results = attack(ct)

    if results:
        best_a, best_b, best_pt = results[0]
        with open("decrypted.txt", "w", encoding="utf-8") as f:
            f.write(best_pt)
        print(f"\nBest key: a={best_a}, b={best_b}")
        print("Decrypted text saved to decrypted.txt\n")
    else:
        print("\nNo meaningful results found.")

    with open("key.txt", "w", encoding="utf-8") as g:
        g.write("\n".join(log_lines))
    print("Key search log saved to key.txt")

if __name__ == "__main__":
    main()
