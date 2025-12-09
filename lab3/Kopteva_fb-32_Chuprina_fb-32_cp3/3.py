import math
from collections import Counter
from pathlib import Path

ALPHABET = "абвгдежзийклмнопрстуфхцчшщьыэюя"  # 31 буква
M = len(ALPHABET)
MOD = M * M  # 31^2 = 961

LANG_TOP5_BIGRAMS = ["ст", "но", "то", "на", "ен"]

alpha_set = set(ALPHABET)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("ё", "е").replace("ъ", "ь")
    text = "".join(ch for ch in text if ch in alpha_set)
    return text

def charmap():
    char2i = {ch: i for i, ch in enumerate(ALPHABET)}
    i2char = {i: ch for ch, i in char2i.items()}
    return char2i, i2char

char2i, i2char = charmap()

def bigram_to_num(bg: str) -> int:
    return char2i[bg[0]] * M + char2i[bg[1]]

def num_to_bigram(x: int) -> str:
    return i2char[(x // M) % M] + i2char[x % M]

def split_non_overlapping(s: str):
    n = len(s) // 2 * 2
    return [s[i:i + 2] for i in range(0, n, 2)]

def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def invmod(a, m):
    a %= m
    g, x, y = egcd(a, m)
    if g != 1:
        raise ValueError("No inverse")
    return x % m

def solve_linear_congruence(A, B, mod):
    A %= mod
    B %= mod
    g = math.gcd(A, mod)
    if B % g != 0:
        return []
    A1, B1, M1 = A // g, B // g, mod // g
    inv = invmod(A1, M1)
    x0 = (inv * B1) % M1
    return [(x0 + k * M1) % mod for k in range(g)]

def index_of_coincidence(s: str) -> float:      #індекс збігів
    n = len(s)
    if n < 2:
        return 0.0
    cnt = Counter(s)
    return sum(c * (c - 1) for c in cnt.values()) / (n * (n - 1))

def compute_bigram_counts_nonoverlap(text: str):
    bigs = split_non_overlapping(text)
    cnt = Counter(bigs)
    total = sum(cnt.values()) or 1
    rows = []
    for bg, c in cnt.most_common():
        rows.append({"bigram": bg, "count": c, "freq": c / total})
    return rows

def generate_candidates(cipher_top5, lang_top5=LANG_TOP5_BIGRAMS):
    from itertools import permutations
    candidates = set()
    details = []

    for X1, X2 in permutations(lang_top5, 2):
        x1, x2 = bigram_to_num(X1), bigram_to_num(X2)
        dX = (x1 - x2) % MOD

        for Y1, Y2 in permutations(cipher_top5, 2):
            y1, y2 = bigram_to_num(Y1), bigram_to_num(Y2)
            dY = (y1 - y2) % MOD

            sols = solve_linear_congruence(dX, dY, MOD)
            for a in sols:
                if math.gcd(a, MOD) != 1:
                    continue
                b = (y1 - a * x1) % MOD
                candidates.add((a, b))
                details.append(
                    {"lang_pair": f"{X1}->{Y1}, {X2}->{Y2}", "a": a, "b": b}
                )

    return sorted(list(candidates)), details


def decrypt_with_key(text: str, a: int, b: int) -> str:

    inva = invmod(a, MOD)
    bigs = split_non_overlapping(text)
    res = []
    for bg in bigs:
        if len(bg) != 2:
            continue
        Y = bigram_to_num(bg)
        X = (inva * (Y - b)) % MOD
        res.append(num_to_bigram(X))
    return "".join(res)

def main():
    script_dir = Path(__file__).resolve().parent

    cipher_path = script_dir / "cipher.txt"

    if not cipher_path.exists():
        print(f"[!] Файл з шифртексто не знайдено: {cipher_path}")
        return

    raw_text = cipher_path.read_text(encoding="utf-8", errors="ignore")
    norm = normalize_text(raw_text)
    print(f"[i]Довжина нормалізованого текста: {len(norm)} символов")

    rows = compute_bigram_counts_nonoverlap(norm)
    cipher_top5 = [row["bigram"] for row in rows[:5]]

    print("\n[i] Топ-10 біграм в шифртексте (без перекрыття):")
    for r in rows[:10]:
        print(f"    {r['bigram']!r}: count={r['count']}, freq={r['freq']:.4f}")

    print(f"\n[i] cipher_top5 = {cipher_top5}")

    candidates, details = generate_candidates(cipher_top5)
    print(f"\n[i] Знайдені кандидати на ключі (a,b): {len(candidates)}")

    results = []
    for a, b in candidates:
        try:
            pt = decrypt_with_key(norm, a, b)
        except Exception as e:
            print(f"[!] Помилка при дешифруванні a={a}, b={b}: {e}")
            continue
        ic = index_of_coincidence(pt)
        ic_diff = abs(ic - 0.055)  
        results.append({
            "a": a,
            "b": b,
            "IC": ic,
            "IC_diff": ic_diff,
            "plaintext": pt,
        })

    if not results:
        print("[!] Не вдалося отримати жодного кандидата для розшифровки.")
        return

    results.sort(key=lambda r: r["IC_diff"])

    TOP_SHOW = 5
    print(f"\n[i] {TOP_SHOW} Топ кандидатів по IC:")

    for idx, r in enumerate(results[:TOP_SHOW], start=1):
        print("\n" + "=" * 80)
        print(f"Кандидат #{idx}")
        print(f"a={r['a']}, b={r['b']}, IC={r['IC']:.6f}, |IC-0.055|={r['IC_diff']:.6f}")
        print("-" * 80)
        preview = r["plaintext"][:500]  
        print(preview)
        print("-" * 80)

    best = results[0]
    print("\n" + "#" * 80)
    print("[+] Найкращий кандидат (по IC):")
    print(f"a={best['a']}, b={best['b']}, IC={best['IC']:.6f}, |IC-0.055|={best['IC_diff']:.6f}")
    print("#" * 80)
    print(best["plaintext"][:1000])  

    best_plain_path = script_dir / "best_plaintext_ic.txt"
    best_key_path = script_dir / "best_key_ic.txt"

    best_plain_path.write_text(best["plaintext"], encoding="utf-8")
    best_key_path.write_text(
        f"a={best['a']}, b={best['b']}, IC={best['IC']:.6f}\n",
        encoding="utf-8"
    )

    print(f"\n[i] Найкращий plaintext збережен в: {best_plain_path}")
    print(f"[i] Ключ збережено в: {best_key_path}")

if __name__ == "__main__":
    main()
