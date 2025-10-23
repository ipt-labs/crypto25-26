import math
from collections import Counter
import pandas as pd

RUSSIAN_LETTERS = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯ'  
RUSSIAN_LETTERS_WITH_SPACE = RUSSIAN_LETTERS + ' '  

def filter_text(text, include_spaces=False):
    text = text.upper().replace('Ё', 'Е').replace('Ъ', 'Ь')
    alphabet = RUSSIAN_LETTERS_WITH_SPACE if include_spaces else RUSSIAN_LETTERS
    filtered = []
    prev_space = False
    for char in text:
        if char in RUSSIAN_LETTERS:
            filtered.append(char)
            prev_space = False
        elif include_spaces and char.isspace() and not prev_space:
            filtered.append(' ')
            prev_space = True
    return ''.join(filtered)

def calculate_bigram_frequencies_and_entropy(filtered, alphabet, overlapping):
    bigram_count = Counter()
    step = 1 if overlapping else 2
    for i in range(0, len(filtered) - 1, step):
        bigram = filtered[i] + filtered[i+1]
        bigram_count[bigram] += 1
    total_bigram = sum(bigram_count.values())
    bigram_freq = {a + b: bigram_count.get(a + b, 0) / total_bigram if total_bigram > 0 else 0
                   for a in alphabet for b in alphabet}
    H_bigram = -sum(p * math.log2(p) for p in bigram_freq.values() if p > 0)
    H2 = H_bigram / 2 if total_bigram > 0 else 0
    return bigram_freq, H2


def analyze_file(filename, excel_filename='analysis.xlsx'):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    results = {}
    for include_spaces in [False, True]:
        key = 'з пробілами' if include_spaces else 'без пробілів'
        filtered = filter_text(text, include_spaces)
        alphabet = RUSSIAN_LETTERS_WITH_SPACE if include_spaces else RUSSIAN_LETTERS
        m = len(alphabet)
        H0 = math.log2(m)

        mono_count = Counter(filtered)
        total_mono = len(filtered)
        mono_freq = {letter: mono_count.get(letter, 0) / total_mono if total_mono > 0 else 0 for letter in alphabet}
        H1 = -sum(p * math.log2(p) for p in mono_freq.values() if p > 0)
        R1 = 1 - H1 / H0 if H0 > 0 else 0

        results[key] = {
            'mono_freq': mono_freq,
            'H0': H0,
            'H1': H1,
            'R1': R1,
            'bigram_results': {}
        }

        for overlapping in [True, False]:
            subkey = 'перетинні' if overlapping else 'неперетинні'
            bigram_freq, H2 = calculate_bigram_frequencies_and_entropy(filtered, alphabet, overlapping)
            R2 = 1 - H2 / H0 if H0 > 0 else 0
            results[key]['bigram_results'][subkey] = {
                'bigram_freq': bigram_freq,
                'H2': H2,
                'R2': R2
            }

    metrics_list = []
    for key in results:
        for subkey in results[key]['bigram_results']:
            full_key = f'{key} {subkey}'
            v = results[key]
            bv = v['bigram_results'][subkey]
            metrics_list.append({
                'Модель': full_key,
                'H0': v['H0'],
                'H1': v['H1'],
                'R1': v['R1'],
                'H2': bv['H2'],
                'R2': bv['R2']
            })
    df_metrics = pd.DataFrame(metrics_list)

    with pd.ExcelWriter(excel_filename) as writer:
            df_metrics.to_excel(writer, sheet_name='Метрики та R', index=False)
            for key in results:
                v = results[key]
                df_mono = pd.DataFrame(list(v['mono_freq'].items()), columns=['Символ', 'Частота']).sort_values('Частота', ascending=False)
                df_mono.to_excel(writer, sheet_name=f'Частоти {key}', index=False)
                for subkey, bv in v['bigram_results'].items():
                    full_key = f'{key} {subkey}'
                    alphabet = RUSSIAN_LETTERS_WITH_SPACE if 'пробілами' in key else RUSSIAN_LETTERS
                    bigram_matrix = [[bv['bigram_freq'].get(a + b, 0) for b in alphabet] for a in alphabet]
                    df_bigram = pd.DataFrame(bigram_matrix, index=list(alphabet), columns=list(alphabet))
                    df_bigram.to_excel(writer, sheet_name=f'Біграми {full_key}')
            print(f"Аналіз експортовано до {excel_filename}")

analyze_file("peace_and_war.txt")
