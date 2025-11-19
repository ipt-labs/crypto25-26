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
    for char, count in counts.items():
        prob = count / total_chars
        entropy -= prob * math.log2(prob)
        display_char = 'пробіл' if char == ' ' else char
        freq_table.append({'Символ': display_char, 'Кількість': count, 'Частота': prob})
    df = pd.DataFrame(freq_table).sort_values(by='Кількість', ascending=False)
    return entropy, df

def calculate_h2_overlapping(text):
    bigrams = [text[i:i+2] for i in range(len(text) - 1)]
    total_bigrams = len(bigrams)
    counts = Counter(bigrams)
    joint_entropy = 0
    for bigram, count in counts.items():
        prob = count / total_bigrams
        joint_entropy -= prob * math.log2(prob)
    h2 = joint_entropy / 2
    freq_table = [{'Біграма': b.replace(' ', '_'), 'Кількість': c, 'Частота': c/total_bigrams} for b, c in counts.items()]
    df = pd.DataFrame(freq_table).sort_values(by='Кількість', ascending=False)
    return h2, df

def calculate_h2_non_overlapping(text):
    bigrams = [text[i:i+2] for i in range(0, len(text) - 1, 2)]
    total_bigrams = len(bigrams)
    counts = Counter(bigrams)
    joint_entropy = 0
    for bigram, count in counts.items():
        prob = count / total_bigrams
        joint_entropy -= prob * math.log2(prob)
    h2 = joint_entropy / 2
    freq_table = [{'Біграма': b.replace(' ', '_'), 'Кількість': c, 'Частота': c/total_bigrams} for b, c in counts.items()]
    df = pd.DataFrame(freq_table).sort_values(by='Кількість', ascending=False)
    return h2, df

def print_results(ver_name, h1, h2_over, h2_non_over, df1, df2_over, df2_non_over, top_n_mono=30, top_n_bi=10):
    print(f"\n {ver_name}")
    print(f"H1 (ентропія): {h1:.5f}")
    print(f"H2 (з перетином): {h2_over:.5f}")
    print(f"H2 (без перетину): {h2_non_over:.5f}")
    
    print(f"\nТоп {top_n_mono} символів")
    print(df1.head(top_n_mono).to_string(index=False, formatters={'Частота': '{:.5f}'.format}))
    
    print(f"\nТоп {top_n_bi} біграм (з перетином)")
    print(df2_over.head(top_n_bi).to_string(index=False, formatters={'Частота': '{:.5f}'.format}))
    
    print(f"\nТоп {top_n_bi} біграм (без перетину)")
    print(df2_non_over.head(top_n_bi).to_string(index=False, formatters={'Частота': '{:.5f}'.format}))

try:
    try:
        with open('Unesennye-vetrom.txt', 'r', encoding='cp1251') as f: raw_data = f.read()
    except UnicodeDecodeError:
        with open('Unesennye-vetrom.txt', 'r', encoding='utf-8', errors='ignore') as f: raw_data = f.read()
    print("Зчитування вхідного файлу Unesennye-vetrom.txt")
except FileNotFoundError:
    print("ПОМИЛКА: Файл Unesennye-vetrom.txt не знайдено")
    exit()

text_sp, text_nosp = filter_text(raw_data)
print(f"Текст відфільтровано. Довжина з пробілами: {len(text_sp)}, без пробілів: {len(text_nosp)}")

with open('clean_text_spaces.txt', 'w', encoding='utf-8') as f:
    f.write(text_sp)
with open('clean_text_no_spaces.txt', 'w', encoding='utf-8') as f:
    f.write(text_nosp)

h1_sp, df_h1_sp = calculate_h1(text_sp)
h2_sp_over, df_h2_sp_over = calculate_h2_overlapping(text_sp)
h2_sp_non_over, df_h2_sp_non_over = calculate_h2_non_overlapping(text_sp)

h1_nosp, df_h1_nosp = calculate_h1(text_nosp)
h2_nosp_over, df_h2_nosp_over = calculate_h2_overlapping(text_nosp)
h2_nosp_non_over, df_h2_nosp_non_over = calculate_h2_non_overlapping(text_nosp)

print_results("Результати для версії з пробілами", h1_sp, h2_sp_over, h2_sp_non_over, df_h1_sp, df_h2_sp_over, df_h2_sp_non_over, top_n_mono=30, top_n_bi=10)
print_results("Результати для версії без пробілів", h1_nosp, h2_nosp_over, h2_nosp_non_over, df_h1_nosp, df_h2_nosp_over, df_h2_nosp_non_over, top_n_mono=30, top_n_bi=10)


h0_sp = math.log2(32)
h0_nosp = math.log2(31)

summary = pd.DataFrame({
    'Версія тексту': ['З пробілами', 'Без пробілів'],
    'H1': [h1_sp, h1_nosp],
    'H2 (з перетином)': [h2_sp_over, h2_nosp_over],
    'R (на основі H1)': [1 - h1_sp/h0_sp, 1 - h1_nosp/h0_nosp],
    'R (на основі H2)': [1 - h2_sp_over/h0_sp, 1 - h2_nosp_over/h0_nosp]
})

print("\nПідсумкові результати")
print(summary.to_string(index=False))

with pd.ExcelWriter('lab1_results.xlsx') as writer:
    summary.to_excel(writer, sheet_name='Зведення', index=False)
    df_h1_sp.to_excel(writer, sheet_name='H1 (з пробілами)', index=False)
    df_h1_nosp.to_excel(writer, sheet_name='H1 (без пробілів)', index=False)
    df_h2_sp_over.to_excel(writer, sheet_name='H2 (з перетином, з пробілами)', index=False)
    df_h2_sp_non_over.to_excel(writer, sheet_name='H2 (без перетину, з пробілами)', index=False)
    df_h2_nosp_over.to_excel(writer, sheet_name='H2 (з перетином, без пробілів)', index=False)
    df_h2_nosp_non_over.to_excel(writer, sheet_name='H2 (без перетину, без пробілів)', index=False)

df_h1_sp.to_excel('freq_h1_with_spaces.xlsx', index=False)
df_h1_nosp.to_excel('freq_h1_no_spaces.xlsx', index=False)
df_h2_sp_over.to_excel('freq_h2_overlapping_spaces.xlsx', index=False)
df_h2_sp_non_over.to_excel('freq_h2_non_overlapping_spaces.xlsx', index=False)
df_h2_nosp_over.to_excel('freq_h2_overlapping_no_spaces.xlsx', index=False)
df_h2_nosp_non_over.to_excel('freq_h2_non_overlapping_no_spaces.xlsx', index=False)
