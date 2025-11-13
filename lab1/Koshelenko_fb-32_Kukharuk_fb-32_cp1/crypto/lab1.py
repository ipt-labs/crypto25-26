import re
import math
from collections import Counter

# фільтрація та очистка тексту
def clean_text(text: str) -> str:
    text = text.lower()
    text = text.replace("ё", "е").replace("ъ", "ь")
    text = re.sub(r'[^а-я ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# монограми
def format_num(x):
    if x == 0:
        return "0"
    elif x >= 1e-4:
        return f"{x:.6f}".rstrip("0").rstrip(".")
    else:
        return f"{x:.2e}"

def monograms(text, filename):
    freq = Counter(text)
    total = sum(freq.values())
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Літера,Кількість,Частота\n")
        for ch, cnt in sorted_freq:
            rel_freq = cnt / total
            f.write(f"{ch},{cnt},{format_num(rel_freq)}\n")

# біграми
def bigram_matrix(text, alphabet, filename, step=1):
    bigrams = [text[i:i+2] for i in range(0, len(text)-1, step)]
    freq = Counter(bigrams)
    total = sum(freq.values())
    matrix = {a: {b: 0 for b in alphabet} for a in alphabet}

    for bg, count in freq.items():
        if len(bg) == 2:
            a, b = bg
            matrix[a][b] = count / total

    with open(filename, "w", encoding="utf-8") as f:
        f.write("," + ",".join(alphabet) + "\n")
        for a in alphabet:
            row = ",".join(format_num(matrix[a][b]) for b in alphabet)
            f.write(f"{a},{row}\n")

# ентропія H1 та H2
def H1(text):
    freq = Counter(text)
    total = sum(freq.values())
    H = 0
    for c in freq.values():
        p = c / total
        H -= p * math.log2(p)
    return H

def H2(text, step=1):
    bigrams = [text[i:i+2] for i in range(0, len(text)-1, step)]
    freq = Counter(bigrams)
    total = sum(freq.values())
    H = 0
    for c in freq.values():
        p = c / total
        H -= p * math.log2(p)
    return H / 2

# надлишковість R
def redundancy(H, m):
    return 1 - H / math.log2(m)

# main

def main():
    text_path = "oliver.txt"  

    with open(text_path, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned = clean_text(raw)
    text_with = cleaned
    text_no = cleaned.replace(" ", "")

    with open("with_sp.txt", "w", encoding="utf-8") as f:
        f.write(text_with)
    with open("no_sp.txt", "w", encoding="utf-8") as f:
        f.write(text_no)

    alphabet_with = sorted(set(text_with))
    alphabet_no = sorted(set(text_no))

    # --- монограми ---
    monograms(text_with, "with_sp_mono.csv")
    monograms(text_no, "no_sp_mono.csv")

    # --- біграми ---
    bigram_matrix(text_with, alphabet_with, "with_sp_bi_overlap.csv", step=1)
    bigram_matrix(text_with, alphabet_with, "with_sp_bi_nooverlap.csv", step=2)
    bigram_matrix(text_no, alphabet_no, "no_sp_bi_overlap.csv", step=1)
    bigram_matrix(text_no, alphabet_no, "no_sp_bi_nooverlap.csv", step=2)

    # --- ентропія ---
    H1_with = H1(text_with)
    H1_no = H1(text_no)
    H2_with_overlap = H2(text_with, 1)
    H2_with_nooverlap = H2(text_with, 2)
    H2_no_overlap = H2(text_no, 1)
    H2_no_nooverlap = H2(text_no, 2)

    # --- надлишковість ---
    m_with = 32
    m_no = 31

    results = [
        ("H₁ (з пробілами)", H1_with, redundancy(H1_with, m_with)),
        ("H₂ (з пробілами, overlapped)", H2_with_overlap, redundancy(H2_with_overlap, m_with)),
        ("H₂ (з пробілами, non-overlapped)", H2_with_nooverlap, redundancy(H2_with_nooverlap, m_with)),
        ("H₁ (без пробілів)", H1_no, redundancy(H1_no, m_no)),
        ("H₂ (без пробілів, overlapped)", H2_no_overlap, redundancy(H2_no_overlap, m_no)),
        ("H₂ (без пробілів, non-overlapped)", H2_no_nooverlap, redundancy(H2_no_nooverlap, m_no)),
    ]

    header = (
        f"Результати для тексту: {text_path}\n\n"
        f"{'':40} | {'Ентропія, H (біт/симв.)':>20} | {'Надлишковість, R':>15}\n"
        f"{'-'*82}\n"
    )

    lines = [
        f"{name:40} | {h:>20.10f} | {r:>15.6f}"
        for name, h, r in results
    ]

    output = header + "\n".join(lines)

    
    with open("entropy_redundancy_results.txt", "w", encoding="utf-8") as f:
        f.write(output)

    
    print(output)

    print("\nРоботу завершено. Усі результати збережено у файли:")
    print(" - with_sp_mono.csv, no_sp_mono.csv")
    print(" - with_sp_bi_overlap.csv, with_sp_bi_nooverlap.csv")
    print(" - no_sp_bi_overlap.csv, no_sp_bi_nooverlap.csv")
    print(" - entropy_redundancy_results.txt")


if __name__ == "__main__":
    main()
