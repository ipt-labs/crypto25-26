import math
from collections import Counter
import pandas as pd
import numpy as np
import os

def prepare_text(text, keep_spaces=True):
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')
    alphabet = set('абвгдежзийклмнопрстуфхцчшщыьэюя')
    if keep_spaces:
        alphabet.add(' ')
    filtered = []
    prev_space = False
    for ch in text:
        if ch in alphabet:
            if ch == ' ':
                if not prev_space:
                    filtered.append(ch)
                    prev_space = True
            else:
                filtered.append(ch)
                prev_space = False
        elif keep_spaces and not prev_space:
            filtered.append(' ')
            prev_space = True
    return ''.join(filtered).strip()

def calculate_letter_frequencies(text):
    total = len(text)
    c = Counter(text)
    freqs = {ch: cnt / total for ch, cnt in c.items()}
    return dict(sorted(freqs.items(), key=lambda x: -x[1])), c

def calculate_bigram_frequencies(text, step=1):
    bigrams = [text[i:i+2] for i in range(0, len(text)-1, step)]
    c = Counter(bigrams)
    total = sum(c.values())
    freqs = {bg: cnt / total for bg, cnt in c.items()}
    return freqs, c

def calculate_h1(freqs):
    return -sum(p * math.log2(p) for p in freqs.values() if p > 0)

def calculate_h2(freqs):
    return -0.5 * sum(p * math.log2(p) for p in freqs.values() if p > 0)

def create_bigram_matrix(bigram_counter, alphabet):
    sorted_alpha = sorted(alphabet)
    idx = {ch: i for i, ch in enumerate(sorted_alpha)}
    n = len(sorted_alpha)
    matrix = np.zeros((n, n), dtype=int)
    for bg, count in bigram_counter.items():
        i, j = idx[bg[0]], idx[bg[1]]
        matrix[i, j] = count
    df = pd.DataFrame(matrix, index=sorted_alpha, columns=sorted_alpha)
    return df

def redundancy(H: float, alphabet_size: int) -> float:
    return 0.0 if alphabet_size <= 1 else 1.0 - (H / math.log2(alphabet_size))

def analyze_and_save(filename, with_spaces=True, outdir="results"):
    os.makedirs(outdir, exist_ok=True)
    
    with open(filename, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    print(f"\nАналіз файлу: {filename}")
    print(f"Довжина сирого тексту: {len(raw_text):,} символів")
    
    cleaned = prepare_text(raw_text, keep_spaces=with_spaces)
    print(f"Після фільтрації: {len(cleaned):,} символів")
    
    prefix = "with_spaces" if with_spaces else "no_spaces"
    text_file = os.path.join(outdir, f"clean_{prefix}.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"Збережено очищений текст -> {text_file}")
    
    alphabet = set(cleaned)
    A = len(alphabet)
    
    letter_freqs, _ = calculate_letter_frequencies(cleaned)
    h1 = calculate_h1(letter_freqs)
    r1 = redundancy(h1, A)
    df_monograms = pd.DataFrame(letter_freqs.items(), columns=["Символ", "Ймовірність"])
    
    monograms_path = os.path.join(outdir, f"monogram_{prefix}.xlsx")
    df_monograms.to_excel(monograms_path, index=False)
    
    for step in (1, 2):
        freqs, cnt = calculate_bigram_frequencies(cleaned, step=step)
        h2 = calculate_h2(freqs)
        r2 = redundancy(h2, A)
        if step == 1:
            h2_1, r2_1 = h2, r2
        else:
            h2_2, r2_2 = h2, r2
        
        matrix = create_bigram_matrix(cnt, alphabet)
        matrix_path = os.path.join(outdir, f"bigram_{prefix}_{step}.xlsx")
        matrix.to_excel(matrix_path, index=True)
    
    print("\n - ЕНТРОПІЇ:")
    print(f"H1 = {h1:.6f}")
    print(f"H2 (перекривні)  = {h2_1:.6f}")
    print(f"H2 (неперекривні)= {h2_2:.6f}")
    
    print("\n - НАДЛИШКОВОСТІ:")
    print(f"|A| = {A}, log2(|A|) = {math.log2(A):.6f}")
    print(f"R1 (H1) = {r1:.6f}")
    print(f"R2 (H2, перекривні) = {r2_1:.6f}")
    print(f"R2 (H2, неперекривні) = {r2_2:.6f}")
    
    return {"H1": h1, "R1": r1,
            "H2_step1": h2_1, "R2_step1": r2_1, 
            "H2_step2": h2_2, "R2_step2": r2_2}

if __name__ == "__main__":
    filename = "prestuplenie-i-nakazanie-fedor-dostoevskij.txt"

    print("АНАЛІЗ ТЕКСТУ: «Злочин і кара» Ф.М. Достоєвського")
    print("="*70)

    print("\n --- ТЕКСТ З ПРОБІЛАМИ --- ")
    res1 = analyze_and_save(filename, with_spaces=True)

    print("\n --- ТЕКСТ БЕЗ ПРОБІЛІВ --- ")
    res2 = analyze_and_save(filename, with_spaces=False)

    print("\n================ ПОРІВНЯННЯ РЕЗУЛЬТАТІВ ================")
    print(f"{'Параметр':<25} | {'З пробілами':>14} | {'Без пробілів':>14}")
    print("-"*60)
    print(f"{'H1':<25} | {res1['H1']:>14.6f} | {res2['H1']:>14.6f}")
    print(f"{'H2 (перекривні)':<25} | {res1['H2_step1']:>14.6f} | {res2['H2_step1']:>14.6f}")
    print(f"{'H2 (неперекривні)':<25} | {res1['H2_step2']:>14.6f} | {res2['H2_step2']:>14.6f}")
    print(f"{'R1 (H1)':<25} | {res1['R1']:>14.6f} | {res2['R1']:>14.6f}")
    print(f"{'R2 (H2, перекривні)':<25} | {res1['R2_step1']:>14.6f} | {res2['R2_step1']:>14.6f}")
    print(f"{'R2 (H2, неперекривні)':<25} | {res1['R2_step2']:>14.6f} | {res2['R2_step2']:>14.6f}")
    print("="*70)
    print("\nУсі результати збережено в теці 'results/'")