import math
import pandas as pd
from collections import Counter
from decimal import Decimal

def clean_text(text, isSpace=False):
    bigletter = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ '
    letter = bigletter.lower()
    cleaned = ''.join(ch for ch in text if ch in bigletter + letter).lower()
    if not isSpace:
        cleaned = cleaned.replace(' ', '')
    return cleaned, letter

def calculate_letter_frequencies(text, alphabet):
    total_letters = len(text)
    letter_count = Counter(text)
    return {k: v / total_letters for k, v in letter_count.items() if k in alphabet}

def calculate_bigram_frequencies(text):
    n = len(text)
    bigram_overlap = Counter((text[i], text[i + 1]) for i in range(n - 1))
    bigram_non_overlap = Counter((text[i], text[i + 1]) for i in range(0, n - 1, 2))

    total_overlap = sum(bigram_overlap.values())
    total_non_overlap = sum(bigram_non_overlap.values())

    bigram_freq_overlap = {bg: count / total_overlap for bg, count in bigram_overlap.items()}
    bigram_freq_non_overlap = {bg: count / total_non_overlap for bg, count in bigram_non_overlap.items()}

    return bigram_freq_overlap, bigram_freq_non_overlap

def entropy(freq_dict):
    return -sum(f * math.log2(f) for f in freq_dict.values() if f > 0)

def entropy_bigrams(bigram_freq):
    return entropy(bigram_freq) / 2

def source_redundancy(entropy_value, symbols_count):
    return Decimal(1) - (Decimal(entropy_value) / (Decimal(symbols_count).ln() / Decimal(2).ln()))

def create_bigram_matrix(bigram_freq):
    unique_letters = sorted(set(k[0] for k in bigram_freq.keys()).union(k[1] for k in bigram_freq.keys()))
    matrix = pd.DataFrame(0.0, index=unique_letters, columns=unique_letters)
    for (bg1, bg2), freq in bigram_freq.items():
        matrix.at[bg1, bg2] = round(freq, 3)
    return matrix

def analyze_text(text, isSpace=False):
    cleaned_text, alphabet = clean_text(text, isSpace)

    letter_freq = calculate_letter_frequencies(cleaned_text, alphabet)
    bigram_freq_overlap, bigram_freq_non_overlap = calculate_bigram_frequencies(cleaned_text)

    entropy_h1 = entropy(letter_freq)
    entropy_h2_overlap = entropy_bigrams(bigram_freq_overlap)
    entropy_h2_non_overlap = entropy_bigrams(bigram_freq_non_overlap)

    # Визначаємо розмір алфавіту для R
    symbols_count = len(alphabet) if isSpace else len(alphabet) - 1

    redundancy_h1 = source_redundancy(entropy_h1, symbols_count)
    redundancy_h2_overlap = source_redundancy(entropy_h2_overlap, symbols_count ** 2)
    redundancy_h2_non_overlap = source_redundancy(entropy_h2_non_overlap, symbols_count ** 2)

    return {
        "letter_freq": letter_freq,
        "bigram_overlap": bigram_freq_overlap,
        "bigram_non_overlap": bigram_freq_non_overlap,
        "metrics": {
            "H1": round(entropy_h1, 5),
            "R1": round(redundancy_h1, 5),
            "H2_Перетин": round(entropy_h2_overlap, 5),
            "R2_Перетин": round(redundancy_h2_overlap, 5),
            "H2_Без_Перетин": round(entropy_h2_non_overlap, 5),
            "R2_Без_Перетин": round(redundancy_h2_non_overlap, 5),
        }
    }

def save_results_to_excel(filename, data_with_space, data_without_space):
    with pd.ExcelWriter(filename) as writer:
        pd.DataFrame(list(data_with_space["letter_freq"].items()), columns=['Літера', 'Частота']) \
            .sort_values(by='Частота', ascending=False) \
            .to_excel(writer, sheet_name='Літери (З Пробілами)', index=False)

        pd.DataFrame(list(data_without_space["letter_freq"].items()), columns=['Літера', 'Частота']) \
            .sort_values(by='Частота', ascending=False) \
            .to_excel(writer, sheet_name='Літери (Без Пробілів)', index=False)

        create_bigram_matrix(data_with_space["bigram_overlap"]).to_excel(writer, sheet_name='Біграми_Перетин (З Пробілами)')
        create_bigram_matrix(data_with_space["bigram_non_overlap"]).to_excel(writer, sheet_name='Біграми_Без_Перетину (З Пробілами)')

        create_bigram_matrix(data_without_space["bigram_overlap"]).to_excel(writer, sheet_name='Біграми_Перетин (Без Пробілів)')
        create_bigram_matrix(data_without_space["bigram_non_overlap"]).to_excel(writer, sheet_name='Біграми_Без_Перетину (Без Пробілів)')

        summary_data = {
            "Метрика": ["H1", "R1", "H2_Перетин", "R2_Перетин", "H2_Без_Перетин", "R2_Без_Перетин"],
            "З Пробілами": [str(v).replace('.', ',') for v in data_with_space["metrics"].values()],
            "Без Пробілів": [str(v).replace('.', ',') for v in data_without_space["metrics"].values()],
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Зведена таблиця', index=False)

if __name__ == "__main__":
    with open("text.txt", encoding="utf-8") as file:
        raw_text = file.read()

    analysis_with_space = analyze_text(raw_text, isSpace=True)
    analysis_without_space = analyze_text(raw_text, isSpace=False)

    save_results_to_excel("lab1_results.xlsx", analysis_with_space, analysis_without_space)

    print("Аналіз завершено. Результати збережено у файлі 'lab1_results.xlsx'\n")

    # Вивід метрик у консоль
    print("=== Метрики для тексту З ПРОБІЛАМИ ===")
    for k, v in analysis_with_space["metrics"].items():
        label = k + (" (з пробілом)" if "R" in k else "")
        print(f"{label}: {v}")

    print("\n=== Метрики для тексту БЕЗ ПРОБІЛІВ ===")
    for k, v in analysis_without_space["metrics"].items():
        label = k + (" (без пробілу)" if "R" in k else "")
        print(f"{label}: {v}")
