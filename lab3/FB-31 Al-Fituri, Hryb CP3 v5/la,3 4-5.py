# -*- coding: utf-8 -*-
# Лабораторна 3. Аффінний шифр на біграмах. Пункти 1–5 з повним виводом.
from collections import Counter
from itertools import permutations
import csv

# ===== Загальні константи =====
ALPH = "абвгдежзийклмнопрстуфхцчшщыьэюя"   # 31 літера, 'ё' замінюємо на 'е', без 'ъ'
m = len(ALPH)
M = m * m
POS = {ch: i for i, ch in enumerate(ALPH)}
LANG_TOP = ["ст", "но", "то", "на", "ен"]   # часті біграми рос. мови

# -------------------- 1. Математичні підпрограми --------------------
def extended_gcd(a: int, b: int):
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    d, x1, y1 = extended_gcd(b, a % b)
    return d, y1, x1 - (a // b) * y1

def mod_inverse(a: int, m: int):
    d, x, _ = extended_gcd(a % m, m)
    return (x % m) if d == 1 else None

def solve_linear_congruence(a: int, b: int, m: int):
    a %= m; b %= m
    d, _, _ = extended_gcd(a, m)
    if b % d != 0:
        return []
    a1, b1, m1 = a // d, b // d, m // d
    inv = mod_inverse(a1, m1)
    x0 = (inv * b1) % m1
    return [(x0 + i * m1) % m for i in range(d)]

# -------------------- Утиліти для тексту/біграм --------------------
def clean_text(t: str) -> str:
    t = t.lower().replace("ё", "е")
    return "".join(ch for ch in t if ch in ALPH)

def get_bigrams(t: str):
    t = clean_text(t)
    if len(t) % 2: t = t[:-1]
    return [t[i:i+2] for i in range(0, len(t), 2)]

def bg2num(bg: str) -> int:
    return POS[bg[0]] * m + POS[bg[1]]

def num2bg(x: int) -> str:
    return ALPH[x // m] + ALPH[x % m]

# -------------------- 2. Топ-5 біграм шифртексту --------------------
def top_bigrams_cipher(path: str, top_n: int = 5):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    cnt = Counter(get_bigrams(raw))
    top = cnt.most_common(top_n)
    print(f"\nТоп {top_n} біграм у файлі {path}:")
    for bg, k in top:
        print(f"{bg} — {k} разів")
    return [bg for bg, _ in top]

# -------------------- 3. Генерація кандидатів (a,b) --------------------
def enumerate_key_candidates(cipher_path: str,
                             lang_top=LANG_TOP,
                             top_n_cipher: int = 5):
    top_c = top_bigrams_cipher(cipher_path, top_n_cipher)
    pairs_lang   = list(permutations(lang_top,   2))
    pairs_cipher = list(permutations(top_c,      2))

    seen, out = set(), []
    for X1, X2 in pairs_lang:
        x1, x2 = bg2num(X1), bg2num(X2)
        A = (x1 - x2) % M
        for Y1, Y2 in pairs_cipher:
            y1, y2 = bg2num(Y1), bg2num(Y2)
            B = (y1 - y2) % M
            for a in solve_linear_congruence(A, B, M):
                b = (y1 - a * x1) % M
                if mod_inverse(a, M) is None:   # потрібна інверсія a
                    continue
                if (a, b) not in seen:
                    seen.add((a, b))
                    out.append({"a": a, "b": b, "X*": X1, "X**": X2, "Y*": Y1, "Y**": Y2})
    return out

def print_candidates_table(cands, limit=15, save_csv="candidates_full.csv"):
    header = f"{'№':>2} | {'a':>4} | {'b':>4} | {'X*':^3} | {'X**':^3} | {'Y*':^3} | {'Y**':^3}"
    print("\nКандидати ключа (за a,b):")
    print(header); print("-" * len(header))
    rows = []
    for i, c in enumerate(sorted(cands, key=lambda d: (d['a'], d['b']))[:limit], 1):
        print(f"{i:>2} | {c['a']:>4} | {c['b']:>4} | {c['X*']:^3} | {c['X**']:^3} | {c['Y*']:^3} | {c['Y**']:^3}")
        rows.append([i, c['a'], c['b'], c['X*'], c['X**'], c['Y*'], c['Y**']])
    # повну таблицю збережемо
    with open(save_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["#", "a", "b", "X*", "X**", "Y*", "Y**"])
        all_rows = [[i+1, c['a'], c['b'], c['X*'], c['X**'], c['Y*'], c['Y**']]
                    for i, c in enumerate(sorted(cands, key=lambda d: (d['a'], d['b'])))]
        w.writerows(all_rows)
    print(f"\nЗбережено повну таблицю кандидатів у {save_csv} (рядків: {len(cands)})")

# -------------------- 4. Дешифрування + 5. Автостоп --------------------
def decrypt_affine_bigrams(cipher: str, a: int, b: int) -> str | None:
    inv_a = mod_inverse(a, M)
    if inv_a is None: return None
    t = clean_text(cipher)
    if len(t) % 2: t = t[:-1]
    out = []
    for i in range(0, len(t), 2):
        X = bg2num(t[i:i+2])
        Y = (inv_a * (X - b)) % M
        out.append(num2bg(Y))
    return "".join(out)

def is_meaningful_text(text: str) -> bool:
    t = clean_text(text)
    if len(t) < 200: return False
    freq = Counter(t); total = sum(freq.values())
    if total == 0: return False
    if (freq.get("о",0)+freq.get("а",0)+freq.get("е",0))/total < 0.20: return False
    if (freq.get("ф",0)+freq.get("щ",0)+freq.get("ц",0))/total > 0.05: return False
    bad = ("йй","ьь","ыы","ээ","жы","шы","йы","йь","ьй")
    if any(p in t for p in bad): return False
    bigs = Counter(get_bigrams(t))
    if sum(bigs[b] for b in ("ст","но","то","на","ен")) < 10: return False
    vowels = set("аеёиоуыэюя".replace("ё","е"))
    v = sum(1 for ch in t if ch in vowels)
    c = sum(1 for ch in t if ch in ALPH and ch not in vowels)
    r = v/(v+c) if (v+c) else 0
    return 0.30 <= r <= 0.65

def score_text(s: str) -> float:
    if not s: return -1e9
    n = len(s); cnt = Counter(s)
    top = sum(cnt.get(ch,0)/n for ch in "оеаитнср")
    rare = sum(cnt.get(ch,0)/n for ch in "щфц")
    return 5.0*top - 10.0*max(0.0, rare-0.07)

def try_candidates(cipher_text: str, candidates,
                   show_limit: int = 15, preview_len: int = 30):
    rows = []
    first_ok = None
    best = {"a": None, "b": None, "text": "", "score": -1e9}

    print("\nПеревірка кандидатів на ключ (a, b):")
    print("№ |    a |    b | інверсія |   score   | verdict | preview")
    print("---+------+------+---------+-----------+---------+------------------------------")

    for i, c in enumerate(candidates, 1):
        a, b = c["a"], c["b"]
        inv = mod_inverse(a, M) is not None
        dec = decrypt_affine_bigrams(cipher_text, a, b) if inv else None
        ok = is_meaningful_text(dec) if dec else False
        sc = score_text(dec) if dec else -1e9
        prev = (dec or "")[:preview_len].replace("\n"," ")
        rows.append({"a": a, "b": b, "inverse": inv, "score": f"{sc:.2f}",
                     "ok": ok, "preview": prev})
        if i <= show_limit:
            print(f"{i:2d} | {a:4d} | {b:4d} |   {'yes' if inv else ' no'}   | {sc:10.2f} | "
                  f"{'OK' if ok else 'skip':<7}| {prev}")

        if ok and first_ok is None:
            first_ok = {"a": a, "b": b, "text": dec}
        if sc > best["score"]:
            best = {"a": a, "b": b, "text": dec or "", "score": sc}

    # збереження повної таблиці результатів перевірки
    with open("candidates_full.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    return first_ok if first_ok else best, first_ok is not None

# -------------------- Головний запуск: друк 1–5 --------------------
def run_full_attack(cipher_path: str, show_limit: int = 15):
    # 1. Демонстрація підпрограм
    print("1) Перевірка мат. підпрограм:")
    print("inv(3) mod 7 =", mod_inverse(3,7))
    print("inv(2) mod 4 =", mod_inverse(2,4))
    print("3x ≡ 1 (mod 7)  ->", solve_linear_congruence(3,1,7))
    print("4x ≡ 6 (mod 10) ->", solve_linear_congruence(4,6,10))
    print("6x ≡ 7 (mod 9)  ->", solve_linear_congruence(6,7,9))

    # 2. Топ-5 біграм шифртексту
    top_bigrams_cipher(cipher_path, 5)

    # 3. Генерація кандидатів
    cands = enumerate_key_candidates(cipher_path, LANG_TOP, 5)
    print(f"\nЗгенеровано кандидатів: {len(cands)}")
    print_candidates_table(cands, limit=15, save_csv="candidates_full.csv")

    # 4–5. Перебір кандидатів доти, доки текст не стане осмисленим
    with open(cipher_path, "r", encoding="utf-8") as f:
        cipher_text = f.read()
    best, found_ok = try_candidates(cipher_text, cands, show_limit=show_limit)

    # збереження фіналу
    with open("decrypt_best.txt", "w", encoding="utf-8") as f:
        f.write(best["text"])
    with open("log_best.txt", "w", encoding="utf-8") as f:
        f.write(f"Найкращий ключ (a,b) = ({best['a']}, {best['b']})\n")
        if not found_ok:
            f.write("Увага: жорсткий фільтр не знайшов осмисленого тексту; взято найкращий за score.\n")
        f.write("\nФрагмент:\n" + best["text"][:300])

    print("\n=== РЕЗУЛЬТАТ ===")
    if found_ok:
        print(f"Знайдено осмислений текст при ключі (a, b) = ({best['a']}, {best['b']})")
    else:
        print(f"Осмислений текст не знайдено жорстким фільтром.")
        print(f"Показую найкращий за score ключ (a, b) = ({best['a']}, {best['b']})")
    print("Фрагмент розшифрування:")
    print(best["text"][:300] + ("..." if len(best["text"]) > 300 else ""))
    print("\nФайли: decrypt_best.txt, candidates_full.csv, log_best.txt")

# ---- Точка входу ----
if __name__ == "__main__":
    run_full_attack("cipher.txt", show_limit=15)
