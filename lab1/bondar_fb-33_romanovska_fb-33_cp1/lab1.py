import math
import re
from collections import Counter
import pandas as pd

def clean_text(data: str) -> str:
    text = data.lower()
    text = re.sub(r'[^а-яё\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('ё', 'е').replace('ъ', 'ь')
    return text

def entropy(counter: Counter, total: int) -> float:
    return -sum((freq / total) * math.log2(freq / total)
                for freq in counter.values() if freq > 0)

def redundancy(H_real: float, H_max: float) -> float:
    if H_max == 0:
        return 0.0
    ratio = H_real / H_max
    return 1.0 - ratio

def get_bigrams(text: str, step: int = 1) -> Counter:
    bigram_list = []
    for i in range(0, len(text) - 1, step):
        bigram = text[i : i + 2]
        bigram_list.append(bigram)
    return Counter(bigram_list)

def make_unigram_table(counter: Counter, total: int) -> pd.DataFrame:
    rows = []
    for symbol, count in counter.most_common():
        freq = count / total
        rows.append([symbol, count, freq])
    return pd.DataFrame(rows, columns=["Буква", "Кількість", "Частота"])

def bigram_table(counter: Counter, total: int) -> pd.DataFrame:
    rows = []
    for bigram, count in counter.most_common():
        freq = count / total
        rows.append([bigram, count, freq])
    return pd.DataFrame(rows, columns=["Біграма", "Кількість", "Частота"])

def bigram_matrix(counter: Counter, alphabet: str) -> pd.DataFrame:
    matrix = pd.DataFrame(0, index=list(alphabet), columns=list(alphabet), dtype=float)
    total = sum(counter.values())
    for bigram, count in counter.items():
        if len(bigram) == 2 and bigram[0] in alphabet and bigram[1] in alphabet:
            matrix.loc[bigram[0], bigram[1]] = count / total
    return matrix

def analyze_text(text: str, include_space=True):
    txt = clean_text(text)
    if not include_space:
        txt = txt.replace(' ', '')
    unigrams = Counter(txt)
    total_chars = len(txt)
    H1 = entropy(unigrams, total_chars)
    bigrams_step1 = get_bigrams(txt, step=1)
    bigrams_step2 = get_bigrams(txt, step=2)
    H2_step1 = entropy(bigrams_step1, len(txt) - 1) / 2
    H2_step2 = entropy(bigrams_step2, len(txt) // 2) / 2
    alphabet = 'абвгдежзийклмнопрстуфхцчшщыьэюя' + (' ' if include_space else '')
    H0 = math.log2(len(alphabet))
    results = {
        'H1': H1,
        'H2_step1': H2_step1,
        'H2_step2': H2_step2,
        'R1': redundancy(H1, H0),
        'R2_step1': redundancy(H2_step1, H0),
        'R2_step2': redundancy(H2_step2, H0),
        'unigrams': unigrams,
        'bigrams_step1': bigrams_step1,
        'bigrams_step2': bigrams_step2,
        'total_chars': total_chars,
        'alphabet': alphabet
    }
    return results

def display_results(results: dict, label: str):
    print(f"\n {label.upper()} ")
    print(f"H1 : {results['H1']:.5f}")
    print(f"H2 (крок 1): {results['H2_step1']:.5f}")
    print(f"H2 (крок 2): {results['H2_step2']:.5f}")
    print(f"R (H1): {results['R1']:.5f}")
    print(f"R (H2 крок 1): {results['R2_step1']:.5f}")
    print(f"R (H2 крок 2): {results['R2_step2']:.5f}")

def save_results_to_excel(results_with, results_no):
    with pd.ExcelWriter("results.xlsx") as writer:
        df_uni_with = make_unigram_table(results_with['unigrams'], results_with['total_chars'])
        df_bi1_with = bigram_table(results_with['bigrams_step1'], results_with['total_chars'] - 1)
        df_bi2_with = bigram_table(results_with['bigrams_step2'], results_with['total_chars'] // 2)
        matrix_with = bigram_matrix(results_with['bigrams_step1'], results_with['alphabet'])
        df_uni_with.to_excel(writer, sheet_name="Монограми (з пробілами)", index=False)
        df_bi1_with.to_excel(writer, sheet_name="Біграми крок 1 (з пробілами)", index=False)
        df_bi2_with.to_excel(writer, sheet_name="Біграми крок 2 (з пробілами)", index=False)
        matrix_with.to_excel(writer, sheet_name="Матриця біграм (з пробілами)")
        df_uni_no = make_unigram_table(results_no['unigrams'], results_no['total_chars'])
        df_bi1_no = bigram_table(results_no['bigrams_step1'], results_no['total_chars'] - 1)
        df_bi2_no = bigram_table(results_no['bigrams_step2'], results_no['total_chars'] // 2)
        matrix_no = bigram_matrix(results_no['bigrams_step1'], results_no['alphabet'])
        df_uni_no.to_excel(writer, sheet_name="Монограми (без пробілів)", index=False)
        df_bi1_no.to_excel(writer, sheet_name="Біграми крок 1 (без пробілів)", index=False)
        df_bi2_no.to_excel(writer, sheet_name="Біграми крок 2 (без пробілів)", index=False)
        matrix_no.to_excel(writer, sheet_name="Матриця біграм (без пробілів)")
        summary = pd.DataFrame({
            "Тип": ["З пробілами", "Без пробілів"],
            "H1": [results_with["H1"], results_no["H1"]],
            "H2 (крок 1)": [results_with["H2_step1"], results_no["H2_step1"]],
            "H2 (крок 2)": [results_with["H2_step2"], results_no["H2_step2"]],
            "R (H1)": [results_with["R1"], results_no["R1"]],
            "R (H2 крок 1)": [results_with["R2_step1"], results_no["R2_step1"]],
            "R (H2 крок 2)": [results_with["R2_step2"], results_no["R2_step2"]],
        })
        summary.to_excel(writer, sheet_name="Підсумки", index=False)
    print("Результати збережено у файл.")
    
def main():
    path = "./Bulgakov_Mihail_Master_i_Margarita.txt"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Відсутній файл")
        return
    except UnicodeDecodeError:
        print("Проблема з кодуванням.")
        return
    print("Обробка")
    with_spaces = analyze_text(content, include_space=True)
    display_results(with_spaces, "з пробілами")
    no_spaces = analyze_text(content, include_space=False)
    display_results(no_spaces, "без пробілів")
    save_results_to_excel(with_spaces, no_spaces)

if __name__ == "__main__":
    main()