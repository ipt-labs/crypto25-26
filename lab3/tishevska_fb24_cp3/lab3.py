from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import permutations
from typing import Dict, List, Tuple, Optional
import argparse, csv, math, re, os

# =========================
# 0. Налаштування
# =========================
ALPHABET_WITH_SPACE = "абвгдежзийклмнопрстуфхцчшщыьэюя "
ALPHABET_NO_SPACE   = "абвгдежзийклмнопрстуфхцчшщыьэюя"   
M   = len(ALPHABET_NO_SPACE)
MOD = M * M                                              
LANG_TOP5 = ("ст","но","то","на","ен")                  

# =========================
# 1. Математичні підпрограми
# =========================
def egcd(a: int, b: int):
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def inv_mod(a: int, n: int) -> Optional[int]:
    a %= n
    g, x, _ = egcd(a, n)
    return (x % n) if g == 1 else None

def solve_linear_congruence(a: int, b: int, n: int) -> List[int]:
    a %= n; b %= n
    g = math.gcd(a, n)
    if b % g != 0:
        return []
    if g == 1:
        ia = inv_mod(a, n)
        return [(ia * b) % n] if ia is not None else []
    a1, b1, n1 = a // g, b // g, n // g
    ia1 = inv_mod(a1, n1)
    if ia1 is None:
        return []
    x0 = (ia1 * b1) % n1
    return [(x0 + k * n1) % n for k in range(g)]

# =========================
# 2. Програма з Лаби-1: читання/нормалізація/підрахунок біграм
# =========================
def read_text_auto(path: str) -> str:
    for enc in ("utf-8","cp1251"):
        try:
            with open(path,"r",encoding=enc) as f: return f.read()
        except UnicodeDecodeError:
            continue
    return open(path,"r",encoding="utf-8",errors="ignore").read()

def normalize_with_space(raw: str) -> str:
    t = raw.replace("ё","е").replace("Ё","Е").replace("ъ","ь").replace("Ъ","Ь").lower()
    t = re.sub(r"[^а-я\s]"," ",t)
    t = re.sub(r"\s+"," ",t).strip()
    return t

def remove_spaces(text: str) -> str:
    return text.replace(" ","")

def monogram_counts(text: str) -> Counter:
    return Counter(text)

def counts_to_freqs(counts: Dict[str,int], total: int) -> Dict[str,float]:
    if total == 0: return {}
    return {k: v/total for k,v in counts.items()}

def bigram_counts(text: str, step: int) -> Dict[str,int]:
    res: Dict[str,int] = defaultdict(int)
    for i in range(0, len(text)-1, step):
        bg = text[i:i+2]
        if len(bg)==2: res[bg]+=1
    return dict(res)

# =========================
# 3. Афінний на біграмах (утиліти)
# =========================
L2I = {ch:i for i,ch in enumerate(ALPHABET_NO_SPACE)}
I2L = {i:ch for ch,i in L2I.items()}

def bigram_to_num(bg: str) -> int:
    return L2I[bg[0]]*M + L2I[bg[1]]

def num_to_bigram(x: int) -> str:
    return I2L[(x//M)%M] + I2L[x%M]

def normalize_no_space_for_cipher(raw: str) -> str:
    t = raw.lower().replace("ё","е").replace("ъ","ь")
    return "".join(ch for ch in t if ch in L2I)

# =========================
# 4. топ-5 неперетинних біграм шифртексту
# =========================
def top5_non_overlapping_bigrams(cipher_no_space: str) -> List[Tuple[str,int]]:
    c = Counter()
    end = len(cipher_no_space) - (len(cipher_no_space)%2)
    for i in range(0, end, 2):
        c[cipher_no_space[i:i+2]] += 1
    return c.most_common(5)

# =========================
# 5. кандидати (a,b) із пар top-5
# =========================
def a_candidates(lang_pair: Tuple[str,str], ciph_pair: Tuple[str,str]) -> List[int]:
    X1,X2 = bigram_to_num(lang_pair[0]), bigram_to_num(lang_pair[1])
    Y1,Y2 = bigram_to_num(ciph_pair[0]), bigram_to_num(ciph_pair[1])
    dX = (X1 - X2) % MOD
    dY = (Y1 - Y2) % MOD
    sols = solve_linear_congruence(dX, dY, MOD)  
    return [a for a in sols if math.gcd(a, MOD) == 1]

def b_from_a(lang_bg: str, ciph_bg: str, a: int) -> int:
    return (bigram_to_num(ciph_bg) - a*bigram_to_num(lang_bg)) % MOD

def enumerate_candidate_keys_with_details(cipher_top5: List[str],
                                          max_console_rows: int = 30) -> Tuple[List[Tuple[int,int]], List[List]]:
    uniq = set()
    detailed_rows: List[List] = []
    shown = 0

    print("\n=== Пункт 3. Детальна побудова кандидатів (a,b) ===")
    print("Формула: a * (X1 - X2) ≡ (Y1 - Y2) (mod 961),  b = (Y1 - a*X1) mod 961\n")

    for lp in permutations(LANG_TOP5, 2):        
        for cp in permutations(cipher_top5, 2):  
            a_list = a_candidates(lp, cp)
            if not a_list:
                continue
            if shown < max_console_rows:
                dX = (bigram_to_num(lp[0]) - bigram_to_num(lp[1])) % MOD
                dY = (bigram_to_num(cp[0]) - bigram_to_num(cp[1])) % MOD
                print(f"Мова {lp}  →  Шифр {cp}")
                print(f"  dX={dX}, dY={dY}")
            for a in a_list:
                b = b_from_a(lp[0], cp[0], a)
                uniq.add((a, b))
                detailed_rows.append([lp[0], lp[1], cp[0], cp[1], a, b])
                if shown < max_console_rows:
                    print(f"    a={a:>3}, b={b:>3}")
            if shown < max_console_rows:
                print()
            shown += 1

    print(f"Згенеровано унікальних кандидатів ключа: {len(uniq)}")
    return sorted(list(uniq)), detailed_rows

# =========================
# 6. Крок 4–5: дешифрування + оцінка “російськості”
# =========================
def decrypt_bigrams(cipher_no_space: str, a: int, b: int) -> Optional[str]:
    inv_a = inv_mod(a, MOD)
    if inv_a is None: return None
    end = len(cipher_no_space) - (len(cipher_no_space)%2)
    out=[]
    for i in range(0, end, 2):
        Y = bigram_to_num(cipher_no_space[i:i+2])
        X = (inv_a*(Y - b)) % MOD
        out.append(num_to_bigram(X))
    return ''.join(out)

COMMON_RU = set("оеаинтсрвлк")
FREQ_BG   = {"ст","но","то","на","ен","ни","ра","ко","ос","ер","пр","ро","ти","ль"}
BAD_BG    = {"йй","ыы","ьь"}

def russian_score(s: str) -> float:
    if not s: return -1e9
    n = len(s)
    p_common = sum(1 for ch in s if ch in COMMON_RU) / n
    bgs = [s[i:i+2] for i in range(len(s)-1)]
    p_freq = (sum(1 for b in bgs if b in FREQ_BG)/len(bgs)) if bgs else 0.0
    bad = sum(1 for b in bgs if b in BAD_BG)
    return 3.0*p_common + 2.0*p_freq - 0.5*bad

# =========================
# 7. Головний процес
# =========================
@dataclass
class Options:
    cipher_path: str
    top_show: int = 12
    save_best: str = "відкритийтекст.txt"   
    save_all: Optional[str] = None         
    print_best: bool = True
    show_pairs: int = 30                    

def run(opts: Options):
    
    raw = read_text_auto(opts.cipher_path)
    text_sp  = normalize_with_space(raw)
    cipher_ns= remove_spaces(text_sp)

    
    print("Найчастіші біграми мови:", ", ".join(LANG_TOP5))

    
    top5 = top5_non_overlapping_bigrams(cipher_ns)
    cipher_top5 = [bg for bg,_ in top5]
    print("\nТоп-5 неперетинних біграм шифртексту:")
    for bg,cnt in top5:
        print(f"  {bg}: {cnt}")

  
    keys, detailed_rows = enumerate_candidate_keys_with_details(cipher_top5, max_console_rows=opts.show_pairs)
    with open("candidates_step3.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["lang_bg1","lang_bg2","cipher_bg1","cipher_bg2","a","b"])
        w.writerows(detailed_rows)
    print("Повну таблицю кандидатів збережено у: candidates_step3.csv")

    
    scored: List[Tuple[float, Tuple[int,int], str]] = []
    for a,b in keys:
        pt = decrypt_bigrams(cipher_ns, a, b)
        if not pt: continue
        scored.append((russian_score(pt),(a,b),pt))
    scored.sort(key=lambda t: t[0], reverse=True)

   
    print(f"\nТОП-{min(opts.top_show,len(scored))} кандидатів за метрикою:")
    for i,(sc,(a,b),pt) in enumerate(scored[:opts.top_show],1):
        print(f"{i:>2}. score={sc:.4f}  a={a}  b={b}  | {pt[:140].replace(chr(10),' ')}")

    
    if scored:
        best_text = scored[0][2]
        if opts.print_best:
            print("\n=== ВІДКРИТИЙ ТЕКСТ ===")
            print(best_text)
        if opts.save_best:
            with open(opts.save_best, "w", encoding="utf-8") as f:
                f.write(best_text)
            print(f"\nЗбережено найкращий відкртий текст у: {opts.save_best}")

   
    if opts.save_all:
        with open(opts.save_all, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["a","b","score","plaintext"])
            for sc,(a,b),pt in scored:
                w.writerow([a,b,f"{sc:.6f}",pt])
        print(f"Збережено усі дешифрування у: {opts.save_all}")

# =========================
# 8. CLI
# =========================
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cipher", type=str, default="05.txt")
    p.add_argument("--top", type=int, default=12)
    p.add_argument("--save-best", type=str, default="відкритийтекст.txt")
    p.add_argument("--save-all", type=str, default=None)
    p.add_argument("--show-pairs", type=int, default=30)
    p.add_argument("--no-print-best", action="store_true")
    args = p.parse_args()
    run(Options(
        cipher_path=args.cipher,
        top_show=args.top,
        save_best=args.save_best,
        save_all=args.save_all,
        print_best=(not args.no_print_best),
        show_pairs=args.show_pairs
    ))

if __name__ == "__main__":
    main()
