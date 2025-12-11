import math
import pandas as pd
from collections import Counter
import re


def preprocess(txt, spaces=True):
    """Нормалізація тексту: lower case, заміна символів, фільтрація"""
    txt = txt.lower().replace('ё', 'е').replace('ъ', 'ь')
    pattern = r'[^а-яіїє\s]' if spaces else r'[^а-яіїє]'
    txt = re.sub(pattern, ' ' if spaces else '', txt)
    return re.sub(r'\s+', ' ', txt).strip() if spaces else txt


def char_freq(txt):
    """Частоти символів"""
    return Counter(txt)


def bigram_freq(txt, overlap=True):
    """Частоти біграм (overlap=True для перетину)"""
    step = 1 if overlap else 2
    return Counter(txt[i:i+2] for i in range(0, len(txt) - 1, step))


def entropy(freq, total):
    """Обчислення ентропії за формулою Шеннона"""
    return -sum((c/total) * math.log2(c/total) for c in freq.values() if c > 0)


def h1(txt):
    """Ентропія на символ (модель 1-грам)"""
    f = char_freq(txt)
    return entropy(f, len(txt))


def h2(txt):
    """Ентропія на символ (модель біграм)"""
    bf = bigram_freq(txt)
    return entropy(bf, sum(bf.values())) / 2


def bigram_matrix(txt):
    """Матриця частот біграм"""
    bf = bigram_freq(txt)
    alpha = sorted(set(txt))
    mat = pd.DataFrame(0, index=alpha, columns=alpha)
    
    for bg, cnt in bf.items():
        if len(bg) == 2:
            mat.loc[bg[0], bg[1]] = cnt
    
    return mat


def analyze(fname):
    """Головна функція: читання, аналіз, експорт"""
    # Автовизначення кодування
    for enc in ['utf-8', 'windows-1251', 'cp1251', 'koi8-r', 'iso-8859-5']:
        try:
            with open(fname, 'r', encoding=enc) as f:
                raw = f.read()
            print(f"✓ Файл прочитано ({enc})")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Не вдалося прочитати файл")
    
    print(f"Вихідний текст: {len(raw)} символів")
    
    # Обробка з пробілами і без
    txt_sp = preprocess(raw, spaces=True)
    txt_no = preprocess(raw, spaces=False)
    
    print(f"З пробілами: {len(txt_sp)} символів")
    print(f"Без пробілів: {len(txt_no)} символів")
    
    # Частоти
    freq_sp = char_freq(txt_sp)
    freq_no = char_freq(txt_no)
    bg_ov = bigram_freq(txt_sp, overlap=True)
    bg_nv = bigram_freq(txt_sp, overlap=False)
    
    # Розмір алфавіту
    m_sp = len(freq_sp)
    m_no = len(freq_no)
    
    print(f"\nАлфавіт з пробілами: {m_sp}")
    print(f"Алфавіт без пробілів: {m_no}")
    
    # Ентропії
    h0_sp = math.log2(m_sp)
    h0_no = math.log2(m_no)
    h1_sp = h1(txt_sp)
    h1_no = h1(txt_no)
    h2_sp = h2(txt_sp)
    h2_no = h2(txt_no)
    
    print(f"\n=== З ПРОБІЛАМИ ===")
    print(f"H0: {h0_sp:.6f} біт")
    print(f"H1: {h1_sp:.6f} біт")
    print(f"H2: {h2_sp:.6f} біт")
    
    print(f"\n=== БЕЗ ПРОБІЛІВ ===")
    print(f"H0: {h0_no:.6f} біт")
    print(f"H1: {h1_no:.6f} біт")
    print(f"H2: {h2_no:.6f} біт")
    
    # Надлишковість
    r1_sp = 1 - h1_sp/h0_sp
    r1_no = 1 - h1_no/h0_no
    r2_sp = 1 - h2_sp/h0_sp
    r2_no = 1 - h2_no/h0_no
    
    print(f"\n=== НАДЛИШКОВІСТЬ ===")
    print(f"R1 (з пробілами): {r1_sp:.6f} ({r1_sp*100:.2f}%)")
    print(f"R1 (без пробілів): {r1_no:.6f} ({r1_no*100:.2f}%)")
    print(f"R2 (з пробілами): {r2_sp:.6f} ({r2_sp*100:.2f}%)")
    print(f"R2 (без пробілів): {r2_no:.6f} ({r2_no*100:.2f}%)")
    
    # Експорт в Excel
    export_excel(raw, txt_sp, txt_no, freq_sp, freq_no, bg_ov, bg_nv,
                 h0_sp, h0_no, h1_sp, h1_no, h2_sp, h2_no,
                 r1_sp, r1_no, r2_sp, r2_no, m_sp, m_no)
    
    print("\n✓ Експортовано в 'entropy_results.xlsx'")


def export_excel(raw, txt_sp, txt_no, freq_sp, freq_no, bg_ov, bg_nv,
                 h0_sp, h0_no, h1_sp, h1_no, h2_sp, h2_no,
                 r1_sp, r1_no, r2_sp, r2_no, m_sp, m_no):
    """Експорт усіх результатів у Excel"""
    
    with pd.ExcelWriter('entropy_results.xlsx', engine='openpyxl') as w:
        
        # Аркуш 1: Зведені результати
        df1 = pd.DataFrame({
            'Параметр': [
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
            'Значення': [
                len(raw), len(txt_sp), len(txt_no), m_sp, m_no, '',
                f'{h0_sp:.6f} біт', f'{h1_sp:.6f} біт', f'{h2_sp:.6f} біт', '',
                f'{h0_no:.6f} біт', f'{h1_no:.6f} біт', f'{h2_no:.6f} біт', '',
                f'{r1_sp:.6f} ({r1_sp*100:.2f}%)',
                f'{r1_no:.6f} ({r1_no*100:.2f}%)',
                f'{r2_sp:.6f} ({r2_sp*100:.2f}%)',
                f'{r2_no:.6f} ({r2_no*100:.2f}%)'
            ]
        })
        df1.to_excel(w, sheet_name='Загальні результати', index=False)
        
        # Аркуш 2: Частоти (з пробілами)
        sorted_sp = sorted(freq_sp.items(), key=lambda x: x[1], reverse=True)
        df2 = pd.DataFrame({
            '№': range(1, len(sorted_sp) + 1),
            'Символ': [c if c != ' ' else 'ПРОБІЛ' for c, _ in sorted_sp],
            'Кількість': [cnt for _, cnt in sorted_sp],
            'Частота': [cnt/len(txt_sp) for _, cnt in sorted_sp],
            'Відсоток': [f'{cnt/len(txt_sp)*100:.4f}%' for _, cnt in sorted_sp]
        })
        df2.to_excel(w, sheet_name='Частоти (з пробілами)', index=False)
        
        # Аркуш 3: Частоти (без пробілів)
        sorted_no = sorted(freq_no.items(), key=lambda x: x[1], reverse=True)
        df3 = pd.DataFrame({
            '№': range(1, len(sorted_no) + 1),
            'Символ': [c for c, _ in sorted_no],
            'Кількість': [cnt for _, cnt in sorted_no],
            'Частота': [cnt/len(txt_no) for _, cnt in sorted_no],
            'Відсоток': [f'{cnt/len(txt_no)*100:.4f}%' for _, cnt in sorted_no]
        })
        df3.to_excel(w, sheet_name='Частоти (без пробілів)', index=False)
        
        # Аркуш 4: Матриця біграм (перетин)
        mat_ov = bigram_matrix(txt_sp)
        mat_ov.index = [c if c != ' ' else 'ПР' for c in mat_ov.index]
        mat_ov.columns = [c if c != ' ' else 'ПР' for c in mat_ov.columns]
        mat_ov.to_excel(w, sheet_name='Біграми (перетин)')
        
        # Аркуш 5: Матриця біграм (не перетин)
        mat_nv = bigram_matrix(txt_sp)
        for bg, cnt in bg_nv.items():
            if len(bg) == 2 and bg[0] in mat_nv.index and bg[1] in mat_nv.columns:
                mat_nv.loc[bg[0], bg[1]] = cnt
        mat_nv.index = [c if c != ' ' else 'ПР' for c in mat_nv.index]
        mat_nv.columns = [c if c != ' ' else 'ПР' for c in mat_nv.columns]
        mat_nv.to_excel(w, sheet_name='Біграми (не перетин)')
        
        # Аркуш 6: Топ-100 біграм
        top100 = sorted(bg_ov.items(), key=lambda x: x[1], reverse=True)[:100]
        total_bg = sum(bg_ov.values())
        df6 = pd.DataFrame({
            '№': range(1, len(top100) + 1),
            'Біграма': [bg.replace(' ', '_') for bg, _ in top100],
            'Кількість': [cnt for _, cnt in top100],
            'Частота': [cnt/total_bg for _, cnt in top100],
            'Відсоток': [f'{cnt/total_bg*100:.4f}%' for _, cnt in top100]
        })
        df6.to_excel(w, sheet_name='Топ-100 біграм', index=False)


if __name__ == '__main__':
    fname = 'ostrov.txt'  # Змініть на свій файл
    
    try:
        analyze(fname)
    except FileNotFoundError:
        print(f"❌ Файл '{fname}' не знайдено!")
    except Exception as e:
        print(f"❌ Помилка: {e}")