import re
import math
import pandas as pd
from collections import Counter

def filter_text(raw_text):
    text = raw_text.lower()
    text = text.replace('ё', 'е')
    text = text.replace('ъ', 'ь')
    text = re.sub(r'[^а-я]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text_with_spaces = text.strip()
    text_without_spaces = text_with_spaces.replace(' ', '')
    return text_with_spaces, text_without_spaces

def calculate_h1(text):
    total_chars = len(text)
    counts = Counter(text)
    entropy = 0
    freq_table = []
    
    if ' ' in counts:
        h0 = 5.0 
    else:
        h0 = 4.954196 
    
    for char, count in counts.items():
        prob = count / total_chars
        entropy -= prob * math.log2(prob)
        display_char = '<пробіл>' if char == ' ' else char
        freq_table.append({'Символ': display_char, 'Кількість': count, 'Частота': prob})
    
    df = pd.DataFrame(freq_table).sort_values(by='Кількість', ascending=False)
    return entropy, df, h0

def calculate_h2_generic(text, step):
    if len(text) < 2:
        return 0, pd.DataFrame()

    bigrams = [text[i:i+2] for i in range(0, len(text) - 1, step)]
    total_bigrams = len(bigrams)
    counts = Counter(bigrams)
    joint_entropy = 0
    
    freq_list = []
    for bigram, count in counts.items():
        prob = count / total_bigrams
        joint_entropy -= prob * math.log2(prob)
        
        char1 = '<пробіл>' if bigram[0] == ' ' else bigram[0]
        char2 = '<пробіл>' if bigram[1] == ' ' else bigram[1]
        
        freq_list.append({
            'Біграма': bigram.replace(' ', '_'),
            '1-й символ': char1,
            '2-й символ': char2,
            'Кількість': count,
            'Частота': prob
        })
    
    h2 = joint_entropy / 2
    df = pd.DataFrame(freq_list).sort_values(by='Кількість', ascending=False)
    return h2, df

def create_matrix(df):
    if df.empty: return pd.DataFrame()
    matrix = df.pivot_table(index='1-й символ', columns='2-й символ', values='Кількість', fill_value=0)
    return matrix.sort_index(axis=0).sort_index(axis=1)

filename = 'Unesennye-vetrom.txt'
try:
    print(f"Зчитування файлу {filename}")
    try:
        with open(filename, 'r', encoding='cp1251') as f: raw_data = f.read()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f: raw_data = f.read()
except FileNotFoundError:
    print(f"Помилка: файл {filename} не знайдено")
    exit()

text_sp, text_nosp = filter_text(raw_data)
print(f"Довжина тексту (з пробілами): {len(text_sp)}")

print("Збереження відфільтрованого тексту (з пробілами та без)")
with open('clean_text_spaces.txt', 'w', encoding='utf-8') as f:
    f.write(text_sp)
with open('clean_text_no_spaces.txt', 'w', encoding='utf-8') as f:
    f.write(text_nosp)

h1_sp, df_h1_sp, h0_sp = calculate_h1(text_sp)
h1_nosp, df_h1_nosp, h0_nosp = calculate_h1(text_nosp)

h2_sp_over, df_h2_sp_over = calculate_h2_generic(text_sp, step=1)
h2_sp_non_over, df_h2_sp_non_over = calculate_h2_generic(text_sp, step=2)

h2_nosp_over, df_h2_nosp_over = calculate_h2_generic(text_nosp, step=1)
h2_nosp_non_over, df_h2_nosp_non_over = calculate_h2_generic(text_nosp, step=2)

summary = pd.DataFrame({
    'Параметр': [
        'H0 (теоретична)', 
        'H1 (ентропія)', 
        'H2 (з перетином)', 
        'H2 (без перетину)',
        'R (надлишковість за H1)', 
        'R (надлишковість за H2 з перетином)'
    ],
    'З пробілами': [
        h0_sp, h1_sp, h2_sp_over, h2_sp_non_over, 
        1 - h1_sp/h0_sp, 1 - h2_sp_over/h0_sp
    ],
    'Без пробілів': [
        h0_nosp, h1_nosp, h2_nosp_over, h2_nosp_non_over, 
        1 - h1_nosp/h0_nosp, 1 - h2_nosp_over/h0_nosp
    ]
})

print("\nРезультати:")
print(summary.to_string())

print("\nВсі таблиці та матриці збережено в excel-файли")
cols = ['Біграма', 'Кількість', 'Частота']
df_h1_sp.to_excel('freq_h1_with_spaces.xlsx', index=False)
df_h1_nosp.to_excel('freq_h1_no_spaces.xlsx', index=False)
df_h2_sp_over[cols].to_excel('freq_h2_overlapping_spaces.xlsx', index=False)
df_h2_sp_non_over[cols].to_excel('freq_h2_non_overlapping_spaces.xlsx', index=False)
df_h2_nosp_over[cols].to_excel('freq_h2_overlapping_no_spaces.xlsx', index=False)
df_h2_nosp_non_over[cols].to_excel('freq_h2_non_overlapping_no_spaces.xlsx', index=False)
summary.to_excel('lab1_results.xlsx', index=False)

create_matrix(df_h2_sp_over).to_excel('matrix_h2_overlapping_spaces.xlsx', index=True)
create_matrix(df_h2_nosp_over).to_excel('matrix_h2_overlapping_no_spaces.xlsx', index=True)