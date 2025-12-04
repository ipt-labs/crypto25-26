import math
import pandas as pd
from collections import Counter
import re

def preprocess(txt, spaces=True)
    txt = txt.lower().replace('ё', 'е').replace('ъ', 'ь')
    pattern = r'[^а-яіїєs]' if spaces else r'[^а-яіїє]'
    txt = re.sub(pattern, ' ' if spaces else '', txt)
    return re.sub(r's+', ' ', txt).strip() if spaces else txt

def char_freq(txt)
    return Counter(txt)

def bigram_freq(txt, overlap=True)
    step = 1 if overlap else 2
    return Counter(txt[ii+2] for i in range(0, len(txt) - 1, step))

def entropy(freq, total)
    return -sum((ctotal)  math.log2(ctotal) for c in freq.values() if c  0)

def h1(txt)
    f = char_freq(txt)
    return entropy(f, len(txt))

def h2(txt)
    bf = bigram_freq(txt)
    return entropy(bf, sum(bf.values()))  2

def bigram_matrix(txt)
    bf = bigram_freq(txt)
    alpha = sorted(set(txt))
    mat = pd.DataFrame(0, index=alpha, columns=alpha)
    for bg, cnt in bf.items()
        if len(bg) == 2
            mat.loc[bg[0], bg[1]] = cnt
    return mat

def analyze(fname)
    for enc in ['utf-8', 'windows-1251', 'cp1251', 'koi8-r', 'iso-8859-5']
        try
            with open(fname, 'r', encoding=enc) as f
                raw = f.read()
            print(f✓ Файл прочитано ({enc}))
            break
        except UnicodeDecodeError
            continue
    else
        raise ValueError(Не вдалося прочитати файл)
    
    print(fВихідний текст {len(raw)} символів)
    
    txt_sp = preprocess(raw, spaces=True)
    txt_no = preprocess(raw, spaces=False)
    
    print(fЗ пробілами {len(txt_sp)} символів)
    print(fБез пробілів {len(txt_no)} символів)
    
    freq_sp = char_freq(txt_sp)
    freq_no = char_freq(txt_no)
    bg_ov = bigram_freq(txt_sp, overlap=True)
    bg_nv = bigram_freq(txt_sp, overlap=False)
    
    m_sp = len(freq_sp)
    m_no = len(freq_no)
    
    print(fnАлфавіт з пробілами {m_sp})
    print(fАлфавіт без пробілів {m_no})
    
    h0_sp = math.log2(m_sp)
    h0_no = math.log2(m_no)
    h1_sp = h1(txt_sp)
    h1_no = h1(txt_no)
    h2_sp = h2(txt_sp)
    h2_no = h2(txt_no)
    
    print(fn=== З ПРОБІЛАМИ ===)
    print(fH0 (Макс)   {h0_sp.6f} біт)
    print(fH1 (Літери) {h1_sp.6f} біт)
    print(fH2 (Біграми){h2_sp.6f} біт)
    
    print(fn=== БЕЗ ПРОБІЛІВ ===)
    print(fH0 (Макс)   {h0_no.6f} біт)
    print(fH1 (Літери) {h1_no.6f} біт)
    print(fH2 (Біграми){h2_no.6f} біт)
    
    r1_sp = 1 - h1_sph0_sp
    r1_no = 1 - h1_noh0_no
    r2_sp = 1 - h2_sph0_sp
    r2_no = 1 - h2_noh0_no
    
    print(fn=== НАДЛИШКОВІСТЬ ===)
    print(fR1 (з пробілами) {r1_sp.6f} ({r1_sp100.2f}%))
    print(fR1 (без пробілів) {r1_no.6f} ({r1_no100.2f}%))
    print(fR2 (з пробілами) {r2_sp.6f} ({r2_sp100.2f}%))
    print(fR2 (без пробілів) {r2_no.6f} ({r2_no100.2f}%))
    
    export_excel(raw, txt_sp, txt_no, freq_sp, freq_no, bg_ov, bg_nv,
                 h0_sp, h0_no, h1_sp, h1_no, h2_sp, h2_no,
                 r1_sp, r1_no, r2_sp, r2_no, m_sp, m_no)
    
    print(n✓ Експортовано в 'entropy_results.xlsx')

def export_excel(raw, txt_sp, txt_no, freq_sp, freq_no, bg_ov, bg_nv,
                 h0_sp, h0_no, h1_sp, h1_no, h2_sp, h2_no,
                 r1_sp, r1_no, r2_sp, r2_no, m_sp, m_no)
    
    with pd.ExcelWriter('entropy_results.xlsx', engine='openpyxl') as w
        df1 = pd.DataFrame({
            'Параметр' [
                'Довжина вихідного тексту',
                'Довжина з пробілами',
                'Довжина без пробілів',
                'Алфавіт з пробілами',
                'Алфавіт без пробілів',
                '',
                'H0 (з пробілами)',
                'H1 (з пробілами)',
                'H2 (з пробілами)',
                '',
                'H0 (без пробілів)',
                'H1 (без пробілів)',
                'H2 (без пробілів)',
                '',
                'R1 (з пробілами)',
                'R1 (без пробілів)',
                'R2 (з пробілами)',
                'R2 (без пробілів)'
            ],
            'Значення' [
                len(raw), len(txt_sp), len(txt_no), m_sp, m_no, '',
                f'{h0_sp.6f} біт', f'{h1_sp.6f} біт', f'{h2_sp.6f} біт', '',
                f'{h0_no.6f} біт', f'{h1_no.6f} біт', f'{h2_no.6f} біт', '',
                f'{r1_sp.6f} ({r1_sp100.2f}%)',
                f'{r1_no.6f} ({r1_no100.2f}%)',
                f'{r2_sp.6f} ({r2_sp100.2f}%)',
                f'{r2_no.6f} ({r2_no100.2f}%)'
            ]
        })
        df1.to_excel(w, sheet_name='Загальні результати', index=False)
        
        sorted_sp = sorted(freq_sp.items(), key=lambda x x[1], reverse=True)
        df2 = pd.DataFrame({
            '№' range(1, len(sorted_sp) + 1),
            'Символ' [c if c != ' ' else 'ПРОБІЛ' for c, _ in sorted_sp],
            'Кількість' [cnt for _, cnt in sorted_sp],
            'Частота (p)' [cntlen(txt_sp) for _, cnt in sorted_sp],
            'Відсоток' [f'{cntlen(txt_sp)100.4f}%' for _, cnt in sorted_sp]
        })
        df2.to_excel(w, sheet_name='Частоти (з пробілами)', index=False)
        
        sorted_no = sorted(freq_no.items(), key=lambda x x[1], reverse=True)
        df3 = pd.DataFrame({
            '№' range(1, len(sorted_no) + 1),
            'Символ' [c for c, _ in sorted_no],
            'Кількість' [cnt for _, cnt in sorted_no],
            'Частота (p)' [cntlen(txt_no) for _, cnt in sorted_no],
            'Відсоток' [f'{cntlen(txt_no)100.4f}%' for _, cnt in sorted_no]
        })
        df3.to_excel(w, sheet_name='Частоти (без пробілів)', index=False)
        
        mat_ov = bigram_matrix(txt_sp)
        mat_ov.index = [c if c != ' ' else 'ПР' for c in mat_ov.index]
        mat_ov.columns = [c if c != ' ' else 'ПР' for c in mat_ov.columns]
        mat_ov.to_excel(w, sheet_name='Біграми (перетин)')
        
        mat_nv = bigram_matrix(txt_sp) 
        mat_nv[] = 0
        for bg, cnt in bg_nv.items()
            if len(bg) == 2 and bg[0] in mat_nv.index and bg[1] in mat_nv.columns
                mat_nv.loc[bg[0], bg[1]] = cnt
        
        mat_nv.index = [c if c != ' ' else 'ПР' for c in mat_nv.index]
        mat_nv.columns = [c if c != ' ' else 'ПР' for c in mat_nv.columns]
        mat_nv.to_excel(w, sheet_name='Біграми (не перетин)')
        
        top100 = sorted(bg_ov.items(), key=lambda x x[1], reverse=True)[100]
        total_bg = sum(bg_ov.values())
        df6 = pd.DataFrame({
            '№' range(1, len(top100) + 1),
            'Біграма' [bg.replace(' ', '_') for bg, _ in top100],
            'Кількість' [cnt for _, cnt in top100],
            'Частота' [cnttotal_bg for _, cnt in top100],
            'Відсоток' [f'{cnttotal_bg100.4f}%' for _, cnt in top100]
        })
        df6.to_excel(w, sheet_name='Топ-100 біграм', index=False)

if __name__ == '__main__'
    fname = 'ostrov.txt'
    try
        analyze(fname)
    except FileNotFoundError
        print(f Файл '{fname}' не знайдено! Перевірте назву та розташування.)
    except Exception as e
        print(f Помилка {e})