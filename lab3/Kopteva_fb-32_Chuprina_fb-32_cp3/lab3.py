# -*- coding: utf-8 -*-
import os, re, math, json, shutil
from collections import Counter, defaultdict
from pathlib import Path

ALPHABET = "абвгдежзийклмнопрстуфхцчшщьыэюя"  # 31 letters (ё->е, ъ->ь)
M = len(ALPHABET)
MOD = M * M  # 31^2 = 961

LANG_TOP5_BIGRAMS = ["ст", "но", "то", "на", "ен"]  # as in the methodical
VOWELS = set("аеёиоуыэюя".replace("ё","е"))  # ё merges to е

FORBIDDEN_BIGRAMS = set([
    "аь","оь","уь","эь","ыь","йь","ьь","ыы","йй","ьй","йы","ьы",
    "жы","шы","ыа","ыо","ыу","ые","яы","юы","эы","ьи","ые","ьь"
])

TYPICAL_FREQ = {
    "о": 0.10, "е": 0.085, "а": 0.08, "и": 0.073, "н": 0.067, "т": 0.063,
    "с": 0.055, "р": 0.047, "в": 0.045, "л": 0.044, "к": 0.034, "м": 0.032
}
RARE_LETTERS = set("щфь")
FREQ_BIGRAMS_FOR_CHECK = ["ст","но","то","на","ен","ра","ко","ни","во","ро"]

OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True, parents=True)

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)

alpha_set = set(ALPHABET)

def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("ё", "е").replace("ъ", "ь")
    text = "".join(ch for ch in text if ch in alpha_set)
    return text

def charmap():
    char2i = {ch:i for i,ch in enumerate(ALPHABET)}
    i2char = {i:ch for ch,i in char2i.items()}
    return char2i, i2char

char2i, i2char = charmap()

def bigram_to_num(bg: str) -> int:
    return char2i[bg[0]] * M + char2i[bg[1]]

def num_to_bigram(x: int) -> str:
    return i2char[(x // M) % M] + i2char[x % M]

def split_non_overlapping(s: str):
    n = len(s) // 2 * 2
    return [ s[i:i+2] for i in range(0, n, 2) ]

def split_overlapping(s: str):
    return [ s[i:i+2] for i in range(len(s)-1) ]

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
    A %= mod; B %= mod
    g = math.gcd(A, mod)
    if B % g != 0:
        return []
    A1, B1, M1 = A // g, B // g, mod // g
    inv = invmod(A1, M1)
    x0 = (inv * B1) % M1
    return [ (x0 + k * M1) % mod for k in range(g) ]

def index_of_coincidence(s: str) -> float:
    n = len(s)
    if n < 2: return 0.0
    cnt = Counter(s)
    return sum(c*(c-1) for c in cnt.values()) / (n*(n-1))

def score_text(s: str) -> dict:
    n = len(s)
    if n == 0: 
        return {"score": -1e9}
    cnt = Counter(s)
    freqs = {ch: cnt.get(ch,0)/n for ch in TYPICAL_FREQ}
    top6_sum = sum(freqs.values())
    rare_sum = sum(cnt.get(ch,0)/n for ch in RARE_LETTERS)
    vowel_ratio = sum(cnt.get(ch,0) for ch in VOWELS) / n
    forb = split_overlapping(s)
    forb_count = sum(1 for bg in forb if bg in FORBIDDEN_BIGRAMS)
    forb_ratio = forb_count / max(1, len(forb))
    over_bigs = Counter(split_overlapping(s))
    freq_bi_sum = sum(over_bigs.get(bg, 0) for bg in FREQ_BIGRAMS_FOR_CHECK) / max(1, len(over_bigs))
    ic = index_of_coincidence(s)
    score = 0.0
    score += 50 * (top6_sum)
    score -= 150 * max(0.0, rare_sum - 0.12)
    if vowel_ratio < 0.32: score -= 50 * (0.32 - vowel_ratio)
    if vowel_ratio > 0.62: score -= 50 * (vowel_ratio - 0.62)
    score -= 300 * forb_ratio
    score += 200 * freq_bi_sum
    score -= 800 * abs(ic - 0.055)
    return {
        "score": score,
        "top6_sum": top6_sum,
        "rare_sum": rare_sum,
        "vowel_ratio": vowel_ratio,
        "forbidden_ratio": forb_ratio,
        "freq_bigram_presence": freq_bi_sum,
        "IC": ic
    }

def compute_bigram_counts_nonoverlap(text: str):
    bigs = split_non_overlapping(text)
    cnt = Counter(bigs)
    total = sum(cnt.values())
    rows = []
    for bg, c in cnt.most_common():
        rows.append({"bigram": bg, "count": c, "freq": c/total})
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
                details.append({"lang_pair": f"{X1}->{Y1}, {X2}->{Y2}", "a": a, "b": b})
    return sorted(list(candidates)), details

def decrypt_with_key(text: str, a: int, b: int) -> str:
    inva = invmod(a, MOD)
    bigs = split_non_overlapping(text)
    res = []
    for bg in bigs:
        Y = bigram_to_num(bg)
        X = (inva * (Y - b)) % MOD
        res.append(num_to_bigram(X))
    return "".join(res)

def process_cipher_file(path: Path, out_dir: Path = OUT_DIR):
    basename = path.stem
    norm = Path(path).read_text(encoding="utf-8", errors="ignore")
    norm = normalize_text(norm)
    (out_dir / f"{basename}_normalized.txt").write_text(norm, encoding="utf-8")

    rows = compute_bigram_counts_nonoverlap(norm)
    import csv
    with (out_dir / f"{basename}_bigrams.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["bigram","count","freq"])
        w.writeheader()
        w.writerows(rows)

    cipher_top5 = [row["bigram"] for row in rows[:5]]
    write_json(out_dir / f"{basename}_top5_cipher.json", cipher_top5)

    candidates, cand_details = generate_candidates(cipher_top5)
    write_json(out_dir / f"{basename}_candidates_raw.json", cand_details)

    ranking = []
    dec_dir = out_dir / f"{basename}_decryptions"
    dec_dir.mkdir(exist_ok=True, parents=True)
    for a, b in candidates:
        try:
            pt = decrypt_with_key(norm, a, b)
        except Exception:
            continue
        metrics = score_text(pt)
        dec_path = dec_dir / f"dec_a{a}_b{b}.txt"
        dec_path.write_text(pt, encoding="utf-8")
        ranking.append({"a": a, "b": b, **metrics, "path": str(dec_path)})

    ranking.sort(key=lambda r: r["score"], reverse=True)
    write_json(out_dir / f"{basename}_ranking.json", ranking[:50])

    if ranking:
        best = ranking[0]
        write_text(out_dir / f"{basename}_best_key.txt", f"a={best['a']}, b={best['b']}\n{best}")
        best_pt = Path(best["path"]).read_text(encoding="utf-8", errors="ignore")
        write_text(out_dir / f"{basename}_plaintext_best.txt", best_pt)


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    data_dir = Path(".")
    for p in data_dir.glob("*.txt"):
        process_cipher_file(p, OUT_DIR)
