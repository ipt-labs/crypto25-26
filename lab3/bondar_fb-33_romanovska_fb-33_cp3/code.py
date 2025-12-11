from collections import Counter
import math

ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
M = len(ALPHABET)
MOD = M * M
PLAIN_COMMON = ["ст", "но", "то", "на", "ен"]


def bigram_to_num(bg: str) -> int:
    return ALPHABET.index(bg[0]) * M + ALPHABET.index(bg[1])


def num_to_bigram(num: int) -> str:
    return ALPHABET[num // M] + ALPHABET[num % M]


def egcd(a: int, b: int):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def modinv(a: int, n: int):
    a %= n
    g, x, y = egcd(a, n)
    if g != 1:
        return None
    return x % n


def solve_linear(a: int, b: int, n: int):
    a %= n
    b %= n
    g, x0, y0 = egcd(a, n)
    if b % g != 0:
        return []
    a1 = a // g
    b1 = b // g
    n1 = n // g
    inv_a1 = modinv(a1, n1)
    if inv_a1 is None:
        return []
    x_base = (inv_a1 * b1) % n1
    return sorted((x_base + k * n1) % n for k in range(g))


def get_non_overlapping_bigrams(text: str):
    return [text[i:i+2] for i in range(0, len(text) - 1, 2)]


def index_of_coincidence(text: str) -> float:
    N = len(text)
    if N <= 1:
        return 0.0
    cnt = Counter(text)
    s = sum(c * (c - 1) for c in cnt.values())
    return s / (N * (N - 1))


def score_russian(text: str) -> float:
    N = len(text)
    if N < 100:
        return -1e9
    ic = index_of_coincidence(text)
    score_ic = -abs(ic - 0.055) * 200
    ob = [text[i:i+2] for i in range(0, len(text) - 1)]
    total_bi = len(ob)
    common = {"ст", "но", "то", "на", "ен"}
    bad = {"йй", "ьь", "ыы", "шш", "жж", "цц"}
    if total_bi == 0:
        return -1e9
    common_count = sum(1 for bg in ob if bg in common)
    bad_count = sum(1 for bg in ob if bg in bad)
    frac_common = common_count / total_bi
    frac_bad = bad_count / total_bi
    score_common = frac_common * 50
    score_bad = -frac_bad * 200
    return score_ic + score_common + score_bad


def decrypt_with_key(text: str, a: int, b: int) -> str:
    inva = modinv(a, MOD)
    if inva is None:
        raise ValueError("a не має оберненого за модулем 961")
    res = []
    for i in range(0, len(text), 2):
        bg = text[i:i+2]
        if len(bg) < 2:
            break
        y = bigram_to_num(bg)
        x = (inva * (y - b)) % MOD
        res.append(num_to_bigram(x))
    return "".join(res)


def main():
    with open("V10.txt", "r", encoding="utf-8") as f:
        raw = f.read()
    cipher = "".join(ch for ch in raw if ch in ALPHABET)

    nonov_bigrams = get_non_overlapping_bigrams(cipher)
    freq = Counter(nonov_bigrams)
    with open("V10_bigrams_top5.txt", "w", encoding="utf-8") as f:
        f.write("Топ-5 біграм шифртексту:\n")
        for bg, c in freq.most_common(5):
            f.write(f"{bg}: {c}\n")

    top5_cipher = [bg for bg, _ in freq.most_common(5)]

    candidate_keys = set()
    for X1bg in PLAIN_COMMON:
        for X2bg in PLAIN_COMMON:
            if X1bg == X2bg:
                continue
            X1 = bigram_to_num(X1bg)
            X2 = bigram_to_num(X2bg)
            dX = (X1 - X2) % MOD

            for Y1bg in top5_cipher:
                for Y2bg in top5_cipher:
                    if Y1bg == Y2bg:
                        continue
                    Y1 = bigram_to_num(Y1bg)
                    Y2 = bigram_to_num(Y2bg)
                    dY = (Y1 - Y2) % MOD

                    sols = solve_linear(dX, dY, MOD)
                    for a in sols:
                        if math.gcd(a, MOD) != 1:
                            continue
                        b = (Y1 - a * X1) % MOD
                        candidate_keys.add((a, b))

    scored = []
    for a, b in candidate_keys:
        try:
            plain = decrypt_with_key(cipher, a, b)
        except Exception:
            continue
        s = score_russian(plain)
        scored.append((s, a, b))

    scored_sorted = sorted(scored, reverse=True)
    best_score, best_a, best_b = scored_sorted[0]

    best_plain = decrypt_with_key(cipher, best_a, best_b)

    with open("V10_decoded.txt", "w", encoding="utf-8") as f:
        f.write(best_plain)

    with open("V10_key.txt", "w", encoding="utf-8") as f:
        f.write(f"a = {best_a}\n")
        f.write(f"b = {best_b}\n")
        f.write(f"score = {best_score}\n")
        f.write(f"IC = {index_of_coincidence(best_plain):.4f}\n")

    print("Готово. Згенеровано файли: V10_bigrams_top5.txt, V10_key.txt, V10_decoded.txt.")


if __name__ == "__main__":
    main()
