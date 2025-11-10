import math
import pandas as pd
from collections import Counter
import re


def clean_text(text, keep_spaces=True):
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')
    pattern = r'[^а-яіїє\s]' if keep_spaces else r'[^а-яіїє]'
    text = re.sub(pattern, ' ' if keep_spaces else '', text)
    return re.sub(r'\s+', ' ', text).strip() if keep_spaces else text


def count_chars(text):
    return Counter(text)


def count_bigrams(text, overlapping=True):
    step = 1 if overlapping else 2
    return Counter(text[i:i+2] for i in range(0, len(text)-1, step))


def calc_entropy(freqs, total):
    return -sum((f/total) * math.log2(f/total) for f in freqs.values() if f > 0)


def monogram_entropy(text):
    freqs = count_chars(text)
    return calc_entropy(freqs, len(text))


def bigram_entropy(text, overlapping=True):
    freqs = count_bigrams(text, overlapping)
    return calc_entropy(freqs, sum(freqs.values())) / 2


def build_matrix(text):
    bg_freqs = count_bigrams(text)
    chars = sorted(set(text))
    matrix = pd.DataFrame(0, index=chars, columns=chars)
    
    for bigram, count in bg_freqs.items():
        if len(bigram) == 2:
            matrix.loc[bigram[0], bigram[1]] = count
    
    return matrix


def process_file(filename):
    encodings = ['utf-8', 'windows-1251', 'cp1251', 'koi8-r']
    
    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as f:
                raw_text = f.read()
            print(f"Файл завантажено ({enc}), символів: {len(raw_text)}")
            break
        except UnicodeDecodeError:
            continue
    
    text_with_sp = clean_text(raw_text, True)
    text_no_sp = clean_text(raw_text, False)
    
    print(f"Після обробки: {len(text_with_sp)} (з пробілами), {len(text_no_sp)} (без)")
    
    # Частоти
    freq_sp = count_chars(text_with_sp)
    freq_no = count_chars(text_no_sp)
    bg_overlap_sp = count_bigrams(text_with_sp, True)
    bg_nonoverlap_sp = count_bigrams(text_with_sp, False)
    bg_overlap_no = count_bigrams(text_no_sp, True)
    bg_nonoverlap_no = count_bigrams(text_no_sp, False)
    
    # Алфавіт
    alphabet_sp = len(freq_sp)
    alphabet_no = len(freq_no)
    
    print(f"\nРозмір алфавіту: {alphabet_sp} (з пробілами), {alphabet_no} (без)")
    
    # Ентропії
    h0_sp = math.log2(alphabet_sp)
    h0_no = math.log2(alphabet_no)
    h1_sp = monogram_entropy(text_with_sp)
    h1_no = monogram_entropy(text_no_sp)
    h2_ov_sp = bigram_entropy(text_with_sp, True)
    h2_nv_sp = bigram_entropy(text_with_sp, False)
    h2_ov_no = bigram_entropy(text_no_sp, True)
    h2_nv_no = bigram_entropy(text_no_sp, False)
    
    print(f"\n--- З пробілами ---")
    print(f"H0: {h0_sp:.6f} біт")
    print(f"H1: {h1_sp:.6f} біт")
    print(f"H2 (перекриття): {h2_ov_sp:.6f} біт")
    print(f"H2 (без перекриття): {h2_nv_sp:.6f} біт")
    
    print(f"\n--- Без пробілів ---")
    print(f"H0: {h0_no:.6f} біт")
    print(f"H1: {h1_no:.6f} біт")
    print(f"H2 (перекриття): {h2_ov_no:.6f} біт")
    print(f"H2 (без перекриття): {h2_nv_no:.6f} біт")
    
    # Надлишковість
    red1_sp = 1 - h1_sp/h0_sp
    red1_no = 1 - h1_no/h0_no
    red2_ov_sp = 1 - h2_ov_sp/h0_sp
    red2_nv_sp = 1 - h2_nv_sp/h0_sp
    red2_ov_no = 1 - h2_ov_no/h0_no
    red2_nv_no = 1 - h2_nv_no/h0_no
    
    print(f"\n--- Надлишковість ---")
    print(f"З пробілами: R1={red1_sp:.4f}, R2(ov)={red2_ov_sp:.4f}, R2(nv)={red2_nv_sp:.4f}")
    print(f"Без пробілів: R1={red1_no:.4f}, R2(ov)={red2_ov_no:.4f}, R2(nv)={red2_nv_no:.4f}")
    
    # Експорт
    save_results(raw_text, text_with_sp, text_no_sp, freq_sp, freq_no,
                 bg_overlap_sp, bg_nonoverlap_sp, bg_overlap_no, bg_nonoverlap_no,
                 h0_sp, h0_no, h1_sp, h1_no, h2_ov_sp, h2_nv_sp, h2_ov_no, h2_nv_no,
                 red1_sp, red1_no, red2_ov_sp, red2_nv_sp, red2_ov_no, red2_nv_no,
                 alphabet_sp, alphabet_no)
    
    print("\nРезультати збережено в 'results.xlsx'")


def save_results(raw, txt_sp, txt_no, freq_sp, freq_no,
                 bg_ov_sp, bg_nv_sp, bg_ov_no, bg_nv_no,
                 h0_sp, h0_no, h1_sp, h1_no, h2_ov_sp, h2_nv_sp, h2_ov_no, h2_nv_no,
                 r1_sp, r1_no, r2_ov_sp, r2_nv_sp, r2_ov_no, r2_nv_no,
                 m_sp, m_no):
    
    with pd.ExcelWriter('results.xlsx', engine='openpyxl') as writer:
        
        # Загальна інформація
        summary = pd.DataFrame({
            'Параметр': [
                'Довжина тексту', 'З пробілами', 'Без пробілів',
                'Алфавіт (з пр)', 'Алфавіт (без пр)', '',
                'H0 (з пр)', 'H1 (з пр)', 'H2 overlap (з пр)', 'H2 non-overlap (з пр)', '',
                'H0 (без пр)', 'H1 (без пр)', 'H2 overlap (без пр)', 'H2 non-overlap (без пр)', '',
                'R1 (з пр)', 'R2 overlap (з пр)', 'R2 non-overlap (з пр)', '',
                'R1 (без пр)', 'R2 overlap (без пр)', 'R2 non-overlap (без пр)'
            ],
            'Значення': [
                len(raw), len(txt_sp), len(txt_no), m_sp, m_no, '',
                f'{h0_sp:.6f}', f'{h1_sp:.6f}', f'{h2_ov_sp:.6f}', f'{h2_nv_sp:.6f}', '',
                f'{h0_no:.6f}', f'{h1_no:.6f}', f'{h2_ov_no:.6f}', f'{h2_nv_no:.6f}', '',
                f'{r1_sp:.4f}', f'{r2_ov_sp:.4f}', f'{r2_nv_sp:.4f}', '',
                f'{r1_no:.4f}', f'{r2_ov_no:.4f}', f'{r2_nv_no:.4f}'
            ]
        })
        summary.to_excel(writer, sheet_name='Загальне', index=False)
        
        # Частоти символів
        chars_sp = sorted(freq_sp.items(), key=lambda x: x[1], reverse=True)
        df_chars_sp = pd.DataFrame({
            'Символ': [c if c != ' ' else 'ПРОБІЛ' for c, _ in chars_sp],
            'Кількість': [cnt for _, cnt in chars_sp],
            'Частота': [cnt/len(txt_sp) for _, cnt in chars_sp]
        })
        df_chars_sp.to_excel(writer, sheet_name='Символи (з пр)', index=False)
        
        chars_no = sorted(freq_no.items(), key=lambda x: x[1], reverse=True)
        df_chars_no = pd.DataFrame({
            'Символ': [c for c, _ in chars_no],
            'Кількість': [cnt for _, cnt in chars_no],
            'Частота': [cnt/len(txt_no) for _, cnt in chars_no]
        })
        df_chars_no.to_excel(writer, sheet_name='Символи (без пр)', index=False)
        
        # Матриці біграм
        matrix_sp = build_matrix(txt_sp)
        matrix_sp.index = [c if c != ' ' else '_' for c in matrix_sp.index]
        matrix_sp.columns = [c if c != ' ' else '_' for c in matrix_sp.columns]
        matrix_sp.to_excel(writer, sheet_name='Матриця біграм (з пр)')
        
        matrix_no = build_matrix(txt_no)
        matrix_no.to_excel(writer, sheet_name='Матриця біграм (без пр)')
        
        # Топ біграм
        top_bg_sp = sorted(bg_ov_sp.items(), key=lambda x: x[1], reverse=True)[:100]
        df_bg_sp = pd.DataFrame({
            'Біграма': [bg.replace(' ', '_') for bg, _ in top_bg_sp],
            'Кількість': [cnt for _, cnt in top_bg_sp],
            'Частота': [cnt/sum(bg_ov_sp.values()) for _, cnt in top_bg_sp]
        })
        df_bg_sp.to_excel(writer, sheet_name='Топ біграм (з пр)', index=False)
        
        top_bg_no = sorted(bg_ov_no.items(), key=lambda x: x[1], reverse=True)[:100]
        df_bg_no = pd.DataFrame({
            'Біграма': [bg for bg, _ in top_bg_no],
            'Кількість': [cnt for _, cnt in top_bg_no],
            'Частота': [cnt/sum(bg_ov_no.values()) for _, cnt in top_bg_no]
        })
        df_bg_no.to_excel(writer, sheet_name='Топ біграм (без пр)', index=False)


if __name__ == '__main__':
    filename = 'ostrov.txt'
    process_file(filename)