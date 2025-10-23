# step3_break_var5.py
# -*- coding: utf-8 -*-
from pathlib import Path
from collections import Counter
import argparse
import sys

# ======= алфавіт (m=32, без "ё") =======
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)
a2i = {ch: i for i, ch in enumerate(ALPHABET)}
i2a = {i: ch for i, ch in enumerate(ALPHABET)}

# орієнтовні частоти рос. (без "ё"), сумарно ≈1.0
RU_FREQ = {
    'о': 0.1097, 'е': 0.0845, 'а': 0.0801, 'и': 0.0735, 'н': 0.0670,
    'т': 0.0626, 'с': 0.0547, 'р': 0.0473, 'в': 0.0454, 'л': 0.0434,
    'к': 0.0349, 'м': 0.0321, 'д': 0.0298, 'п': 0.0281, 'у': 0.0262,
    'я': 0.0201, 'ы': 0.0190, 'ь': 0.0174, 'г': 0.0169, 'з': 0.0164,
    'б': 0.0159, 'ч': 0.0144, 'й': 0.0121, 'х': 0.0097, 'ж': 0.0094,
    'ш': 0.0073, 'ю': 0.0064, 'ц': 0.0048, 'щ': 0.0036, 'э': 0.0032,
    'ф': 0.0026, 'ъ': 0.0004
}

# ======= утиліти =======
def normalize(text: str) -> str:
    t = text.lower().replace("ё", "е")
    return "".join(ch for ch in t if ch in ALPHABET)

def split_by_period(text: str, r: int):
    t = normalize(text)
    return ["".join(t[i] for i in range(j, len(t), r)) for j in range(r)]

def index_of_coincidence(text: str) -> float:
    y = normalize(text)
    n = len(y)
    if n < 2:
        return 0.0
    cnt = Counter(y)
    s = sum(v * (v - 1) for v in cnt.values())
    return s / (n * (n - 1))

def avg_block_ic(text: str, r: int) -> float:
    blocks = split_by_period(text, r)
    ics = [index_of_coincidence(b) for b in blocks if len(b) >= 2]
    return sum(ics) / len(ics) if ics else 0.0

def dr_coincidence(text: str, r: int) -> int:
    t = normalize(text)
    n = len(t)
    if r <= 0 or r >= n:
        return 0
    return sum(1 for i in range(n - r) if t[i] == t[i + r])

def chi_square_shift_score(col_text: str, shift: int) -> float:
    n = len(col_text)
    if n == 0:
        return float('inf')
    cnt = Counter(col_text)
    exp = {ch: RU_FREQ.get(ch, 0.0) * n for ch in ALPHABET}
    cnt_dec = Counter()
    for ych, v in cnt.items():
        yi = a2i[ych]
        xi = (yi - shift) % M
        cnt_dec[i2a[xi]] += v
    chi2 = 0.0
    for ch in ALPHABET:
        O = cnt_dec.get(ch, 0)
        E = exp[ch] if exp[ch] > 1e-12 else 1e-12
        chi2 += (O - E) ** 2 / E
    return chi2

def guess_key_for_period(ciphertext: str, r: int) -> str:
    cols = split_by_period(ciphertext, r)
    key = []
    for col in cols:
        best = min(range(M), key=lambda s: chi_square_shift_score(col, s))
        key.append(i2a[best])
    return "".join(key)

def key_total_score(ciphertext: str, key: str) -> float:
    t = normalize(ciphertext)
    r = len(key)
    cols = split_by_period(t, r)
    shifts = [a2i[ch] for ch in key]
    return sum(chi_square_shift_score(col, shifts[i]) for i, col in enumerate(cols))

def refine_key(ciphertext: str, key: str, passes: int = 3) -> str:
    best_key = list(key)
    best_score = key_total_score(ciphertext, key)
    for _ in range(passes):
        improved = False
        for i in range(len(best_key)):
            orig = best_key[i]
            orig_shift = a2i[orig]
            candidates = [(orig_shift + d) % M for d in range(-6, 7)]
            best_i_shift = orig_shift
            best_i_char = orig
            best_i_score = best_score
            for s in candidates:
                if s == orig_shift:
                    continue
                best_key[i] = i2a[s]
                sc = key_total_score(ciphertext, "".join(best_key))
                if sc < best_i_score:
                    best_i_score = sc
                    best_i_shift = s
                    best_i_char = i2a[s]
            if best_i_char != orig:
                best_key[i] = best_i_char
                best_score = best_i_score
                improved = True
            else:
                best_key[i] = orig
        if not improved:
            break
    return "".join(best_key)

def vigenere_decrypt(ciphertext: str, key: str) -> str:
    c = normalize(ciphertext)
    r = len(key)
    res = []
    for i, ch in enumerate(c):
        y = a2i[ch]
        ki = a2i[key[i % r]]
        x = (y - ki) % M
        res.append(i2a[x])
    return "".join(res)

def search_periods(ciphertext: str, rmin: int, rmax: int):
    t = normalize(ciphertext)
    rows = []
    for r in range(max(2, rmin), rmax + 1):
        rows.append((r, avg_block_ic(t, r), dr_coincidence(t, r)))
    return rows

# ======= plotting (опційно) =======
def try_import_matplotlib():
    try:
        import matplotlib.pyplot as plt
        return plt
    except Exception as e:
        print(f"[plot] matplotlib недоступний: {e}. Пропускаю побудову діаграм.", file=sys.stderr)
        return None

def plot_ic(rows, out_png: str, show: bool):
    plt = try_import_matplotlib()
    if plt is None:
        return
    rs = [r for (r, ic, dr) in rows]
    ics = [ic for (r, ic, dr) in rows]
    plt.figure(figsize=(10, 5))
    plt.plot(rs, ics, marker="o")
    plt.xlabel("Період r")
    plt.ylabel("Середній індекс відповідності (IC)")
    plt.title("IC(r) для шифртексту (Віженер)")
    plt.grid(True)
    if out_png:
        p = Path(out_png)
        plt.tight_layout()
        plt.savefig(p, dpi=150)
        print(f"Діаграму IC збережено у: {p.resolve()}")
    if show:
        plt.show()
    plt.close()

def plot_dr(rows, out_png: str, show: bool):
    plt = try_import_matplotlib()
    if plt is None:
        return
    rs = [r for (r, ic, dr) in rows]
    drs = [dr for (r, ic, dr) in rows]
    plt.figure(figsize=(10, 5))
    plt.bar(rs, drs)
    plt.xlabel("Період r")
    plt.ylabel("D\u1d63(r) — збіги на відстані r")
    plt.title("Dᵣ(r) для шифртексту (Віженер)")
    plt.tight_layout()
    if out_png:
        p = Path(out_png)
        plt.savefig(p, dpi=150)
        print(f"Діаграму Dᵣ збережено у: {p.resolve()}")
    if show:
        plt.show()
    plt.close()

# ======= main =======
def main():
    ap = argparse.ArgumentParser(
        description="Розшифрування Віженера: пошук періоду (IC+Dr) з діаграмами, підбір/уточнення ключа (χ²), дешифрування."
    )
    ap.add_argument("--cipher", default="var5.txt", help="Шлях до шифртексту")
    ap.add_argument("--rmin", type=int, default=2, help="Мінімальна довжина періоду.")
    ap.add_argument("--rmax", type=int, default=40, help="Максимальна довжина періоду.")
    ap.add_argument("--topk", type=int, default=5, help="Скільки кращих r взяти у роботу.")
    ap.add_argument("--outdir", default="результати_завдання_3", help="Каталог для збереження кандидатів.")
    # нові параметри для діаграм
    ap.add_argument("--plot-ic", default="ic_by_r.png", help="PNG для графіка IC(r)")
    ap.add_argument("--plot-dr", default="dr_by_r.png", help="PNG для графіка Dᵣ(r)")
    ap.add_argument("--show", action="store_true", help="Показати вікна з графіками після побудови.")
    args = ap.parse_args()

    cf = Path(args.cipher)
    if not cf.exists():
        print(f"Файл не знайдено: {cf}", file=sys.stderr)
        sys.exit(1)

    ctext = cf.read_text(encoding="utf-8")
    ctext = normalize(ctext)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) оцінка періоду r (IC + Dr)
    rows = search_periods(ctext, args.rmin, args.rmax)

    # --- діаграми ---
    if args.plot_ic:
        plot_ic(rows, str(outdir / args.plot_ic), args.show)
    if args.plot_dr:
        plot_dr(rows, str(outdir / args.plot_dr), args.show)

    # ранжування r: IC (↓ місце) + Dr (↓ місце зі знаком "+")
    by_ic = sorted(rows, key=lambda x: x[1], reverse=True)
    by_dr = sorted(rows, key=lambda x: x[2], reverse=True)
    rank_ic = {r: i for i, (r, _, __) in enumerate(by_ic, start=1)}
    rank_dr = {r: i for i, (r, _, __) in enumerate(by_dr, start=1)}
    scored = [(r, ic, dr, rank_ic[r] + rank_dr[r]) for (r, ic, dr) in rows]
    top = sorted(scored, key=lambda x: x[3])[:args.topk]

    # 2) для кожного топ-r: ключ χ² + локальне уточнення
    summary = ["r,avgIC,Dr,rankSum,key_chi2,key_refined,score_chi2,score_refined,files"]
    best_entry = None
    best_entry_score = float("inf")

    for (r, ic, dr, ranksum) in top:
        key0 = guess_key_for_period(ctext, r)
        key1 = refine_key(ctext, key0, passes=3)
        score0 = key_total_score(ctext, key0)
        score1 = key_total_score(ctext, key1)

        pt0 = vigenere_decrypt(ctext, key0)
        pt1 = vigenere_decrypt(ctext, key1)

        f0 = outdir / f"cand_r{r}_keyCHI2_{key0}.txt"
        f1 = outdir / f"cand_r{r}_keyREF_{key1}.txt"
        f0.write_text(pt0, encoding="utf-8")
        f1.write_text(pt1, encoding="utf-8")

        summary.append(f"{r},{ic:.6f},{dr},{ranksum},{key0},{key1},{score0:.2f},{score1:.2f},{f0.name}|{f1.name}")

        if score1 < best_entry_score:
            best_entry_score = score1
            best_entry = (r, key1, f1)

    # 3) зведення
    (outdir / "таблиця.csv").write_text("\n".join(summary), encoding="utf-8")

    # 4) короткий лог
    print("Топ кандидати (by IC+Dr rank):")
    for row in top:
        print(f"r={row[0]:<3}  IC={row[1]:.6f}  Dr={row[2]:<6}  rankSum={row[3]}")
    if best_entry:
        rbest, kbest, fbest = best_entry
        print(f"\nНайкращий кандидат: r={rbest}, key≈{kbest}")
        print(f"Розшифр збережено у: {fbest.resolve()}")
    print(f"\nЗведення CSV: {(outdir / 'таблиця.csv').resolve()}")

if __name__ == "__main__":
    main()
