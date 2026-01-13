import pandas as pd
import math
import collections
import re

def process_and_analyze(file_path):
    alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"

    results = {}

    for mode in ["with_spaces", "no_spaces"]:
        is_spaces = (mode == "with_spaces")
        current_alpha = alphabet + " " if is_spaces else alphabet
        m = len(current_alpha)
        h0 = math.log2(m)

        # Очищення тексту
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read().lower().replace('ё', 'е').replace('ъ', 'ь')
            if is_spaces:
                text = re.sub(r'[^а-я ]', ' ', text)
                text = re.sub(r'\s+', ' ', text)
            else:
                text = re.sub(r'[^а-я]', '', text)
            text = text.strip()

        # Розрахунок H1 та частот літер
        f1 = collections.Counter(text)
        total1 = sum(f1.values())
        char_freq = {c: f1.get(c, 0)/total1 for c in current_alpha}
        h1 = -sum(p * math.log2(p) for p in char_freq.values() if p > 0)

        # Розрахунок H2 (крок 1 - перетинаються)
        b1 = [text[i:i+2] for i in range(len(text)-1)]
        f2_1 = collections.Counter(b1)
        total2_1 = sum(f2_1.values())
        h2_step1 = -sum((v/total2_1) * math.log2(v/total2_1) for v in f2_1.values()) / 2

        # Розрахунок H2 (крок 2 - не перетинаються)
        b2 = [text[i:i+2] for i in range(0, len(text)-1, 2)]
        f2_2 = collections.Counter(b2)
        total2_2 = sum(f2_2.values())
        h2_step2 = -sum((v/total2_2) * math.log2(v/total2_2) for v in f2_2.values()) / 2

        # Таблиця біграм (крок 1)
        bigram_table = pd.DataFrame(0.0, index=list(current_alpha), columns=list(current_alpha))
        for bg, count in f2_1.items():
            if len(bg) == 2 and bg[0] in current_alpha and bg[1] in current_alpha:
                bigram_table.loc[bg[0], bg[1]] = count / total2_1

        results[mode] = {
            'h1': h1, 'h2_s1': h2_step1, 'h2_s2': h2_step2,
            'r1': 1 - (h1/h0), 'r2': 1 - (h2_step1/h0),
            'char_freq': pd.DataFrame(list(char_freq.items()), columns=['Символ', 'Частота']).sort_values('Частота', ascending=False),
            'bigram_table': bigram_table
        }

    # Збереження в Excel
    with pd.ExcelWriter('lab1/Doroshenko_fb-32_cp1/Lab1_Results.xlsx') as writer:
        summary = pd.DataFrame({
            'Параметр': ['H1', 'H2 (step 1)', 'H2 (step 2)', 'R (H1)', 'R (H2 step 1)'],
            'З пробілами': [results['with_spaces'][k] for k in ['h1', 'h2_s1', 'h2_s2', 'r1', 'r2']],
            'Без пробілів': [results['no_spaces'][k] for k in ['h1', 'h2_s1', 'h2_s2', 'r1', 'r2']]
        })
        summary.to_excel(writer, sheet_name='Підсумки', index=False)
        results['with_spaces']['char_freq'].to_excel(writer, sheet_name='Частоти_з_пробілом', index=False)
        results['no_spaces']['char_freq'].to_excel(writer, sheet_name='Частоти_без_пробілу', index=False)
        results['with_spaces']['bigram_table'].to_excel(writer, sheet_name='Біграми_з_пробілом')
        results['no_spaces']['bigram_table'].to_excel(writer, sheet_name='Біграми_без_пробілу')

process_and_analyze('lab1/Doroshenko_fb-32_cp1/TEXT.txt')
print("Файл Lab1_Results.xlsx створено!")
