import re
from collections import Counter
from itertools import permutations
from math import gcd

alphabet = "абвгдежзийклмнопрстуфхцчшщьыэюя"  
m = len(alphabet)
mod = m * m
A2I = {ch: i for i, ch in enumerate(alphabet)}
I2A = {i: ch for ch, i in A2I.items()}

top_ru_bi = ["ст", "но", "то", "на", "ен"]

#лог для кроків при підборі ключа
LOG = True
_log_lines = []
def log(msg: str):
    if LOG:
        _log_lines.append(msg)

def clean_text(text: str) -> str:
    text = re.sub(f"[^{alphabet}]", "", text)
    if len(text) % 2 == 1:
        text = text[:-1]
    return text

def bigram_to_int(bg: str) -> int:
    return A2I[bg[0]] * m + A2I[bg[1]]

def int_to_bigram(x: int) -> str:
    return I2A[(x // m) % m] + I2A[x % m]

#біграми
def bi_nonoverlap(s: str):
    return [s[i:i+2] for i in range(0, len(s), 2)]

def bi_overlap(s: str):
    return [s[i:i+2] for i in range(len(s)-1)]

def top5_shifr_bi(s: str):
    cnt = Counter(bi_nonoverlap(s))
    return [bg for bg, _ in cnt.most_common(5)]

#математичні операції
def egcd(a: int, b: int):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b != 0:
        q = a // b
        a, b = b, a - q*b
        x0, x1 = x1, x0 - q*x1
        y0, y1 = y1, y0 - q*y1
    return a, x0, y0

def modinv(a: int, n: int):
    a %= n
    g, x, _ = egcd(a, n)
    if g != 1:
        return None
    return x % n

def linear_cong(A: int, B: int, N: int):
    A %= N; B %= N
    g, x, _ = egcd(A, N)
    if B % g != 0:
        return []
    A1, B1, N1 = A // g, B // g, N // g
    invA1 = modinv(A1, N1)
    x0 = (invA1 * B1) % N1
    return [(x0 + k * N1) % N for k in range(g)]

#дешифрування
def decrypt_affine(ct: str, a: int, b: int) -> str | None:
    if gcd(a, m) != 1:
        return None
    inv = modinv(a, mod)
    if inv is None:
        return None
    out = []
    for bg in bi_nonoverlap(ct):
        y = bigram_to_int(bg)
        x = (inv * ((y - b) % mod)) % mod
        out.append(int_to_bigram(x))
    return "".join(out)

#розпізнавач рос мови
freq = set("оеа")
rare = set("фщь")
bad_overlap = {"аь","еь","ыь","оь","яь","юь","ьь","йй"}

def looks_like_ru(s: str) -> bool:
    if not s:
        return False
    n = len(s)
    if s.count("о")/n < 0.10 or s.count("а")/n < 0.07:
        return False
    over = Counter(bi_overlap(s))
    bad = sum(over.get(bg, 0) for bg in bad_overlap)
    if bad > 0:
        return False
    return True

#підбір ключа
def key_candidates(X1: int, X2: int, Y1: int, Y2: int):
    A = (X1 - X2) % mod
    B = (Y1 - Y2) % mod
    ans = []
    sols = linear_cong(A, B, mod)
    log(f"A={A}, B={B} → a_solutions={sols}")
    for a in sols:
        if gcd(a, m) != 1:
            continue
        b = (Y1 - a*X1) % mod
        ans.append((a, b))
    return ans

#атака
def attack(cipher_text: str):
    top_shifr = top5_shifr_bi(cipher_text)
    print("Найчастіші біграми у ШТ:", ", ".join(top_shifr))
    log("top 5 shifr: " + ", ".join(top_shifr))

    X_vals = [bigram_to_int(bg) for bg in top_ru_bi]
    Y_vals = [bigram_to_int(bg) for bg in top_shifr]

    seen = set()
    good = []
    total_pairs = 0

    for (X1, X2) in permutations(X_vals, 2):
        for (Y1, Y2) in permutations(Y_vals, 2):
            total_pairs += 1
            cands = key_candidates(X1, X2, Y1, Y2)
            for a, b in cands:
                if (a, b) in seen:
                    continue
                seen.add((a, b))
                pt = decrypt_affine(cipher_text, a, b)
                if pt and looks_like_ru(pt):
                    good.append((a, b, pt))
                    log(f"pass (a={a}, b={b})")
                else:
                    log(f"fail (a={a}, b={b})")
    print(f"Перебрано пар X/Y: {total_pairs}, отримано кандидатів ключів: {len(seen)}")
    log(f"total_pairs={total_pairs}, candidates={len(seen)}, passed={len(good)}")
    return good

#меін
def main():
    input = "text.txt"
    with open(input, "r", encoding="utf-8") as f:
        raw = f.read()

    ct = clean_text(raw)

    results = attack(ct)

    if results:
        best_a, best_b, best_pt = results[0]
        output = "decrypted.txt"
        with open(output, "w", encoding="utf-8") as g:
            g.write(best_pt)
        print(f"Знайдений ключ: a={best_a}, b={best_b}")

    #лог файл
    if LOG:
        log_out = "steps.txt"
        with open(log_out, "w", encoding="utf-8") as g:
            g.write("\n".join(_log_lines))

if __name__ == "__main__":
    main()