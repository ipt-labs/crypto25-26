import math
import os
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

RUSSIAN_ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

def prepare_text(filepath: Path, keep_spaces: bool = True) -> Optional[str]:
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read().lower()
    except FileNotFoundError:
        print(f"ПОМИЛКА: Файл '{filepath}' не знайдено.")
        return None

    allowed_chars = RUSSIAN_ALPHABET
    if keep_spaces:
        allowed_chars += ' '
    
    cleaned_text = "".join(char for char in text if char in allowed_chars)
    
    if keep_spaces:
        cleaned_text = " ".join(cleaned_text.split())

    return cleaned_text

def get_ngram_frequencies(text: str, n: int = 1, overlapping: bool = True) -> Dict[str, float]:
    step = 1 if overlapping else n
    ngrams = [text[i:i+n] for i in range(0, len(text) - n + 1, step)]
    
    if not ngrams:
        return {}
        
    counts = Counter(ngrams)
    total_ngrams = len(ngrams)
    return {ngram: count / total_ngrams for ngram, count in counts.items()}

def calculate_h1_entropy(letter_frequencies: Dict[str, float]) -> float:
    return -sum(p * math.log2(p) for p in letter_frequencies.values() if p > 0)

def calculate_h2_entropy(
    letter_frequencies: Dict[str, float], bigram_frequencies: Dict[str, float]
) -> float:
    entropy = 0.0
    for bigram, p_ij in bigram_frequencies.items():
        first_char = bigram[0]
        p_i = letter_frequencies.get(first_char)
        if p_ij > 0 and p_i:
            entropy -= p_ij * math.log2(p_ij / p_i)
    return entropy

def save_bigram_matrix_to_csv(
    bigram_freqs: Dict[str, float], alphabet: str, filename: Path
):
    alphabet_list = sorted(list(alphabet))
    df = pd.DataFrame(0.0, index=alphabet_list, columns=alphabet_list)
    
    for bigram, freq in bigram_freqs.items():
        if len(bigram) == 2 and bigram[0] in df.index and bigram[1] in df.columns:
            df.loc[bigram[0], bigram[1]] = freq
            
    df.to_csv(filename, float_format='%.6f')
    print(f"Матриця частот біграм збережена у файл: {filename}")

def run_analysis(text: str, alphabet: str, output_prefix: Path):
    if not text:
        return
        
    separator = "=" * 40
    print(f"\n{separator}\nАНАЛІЗ: {str(output_prefix).upper()}\n{separator}")
    
    letter_freqs = get_ngram_frequencies(text, n=1)
    letter_df = pd.DataFrame(letter_freqs.items(), columns=['Symbol', 'Frequency'])
    letter_df = letter_df.sort_values(by='Frequency', ascending=False)
    letter_filepath = output_prefix.with_name(f"{output_prefix.name}_letter_frequencies.csv")
    letter_df.to_csv(letter_filepath, index=False, float_format='%.6f')
    print(f"Частоти букв збережено у: {letter_filepath}")

    bigram_freqs_overlap = get_ngram_frequencies(text, n=2, overlapping=True)
    save_bigram_matrix_to_csv(
        bigram_freqs_overlap, alphabet, output_prefix.with_name(f"{output_prefix.name}_bigram_matrix_overlapping.csv")
    )
    
    bigram_freqs_no_overlap = get_ngram_frequencies(text, n=2, overlapping=False)
    save_bigram_matrix_to_csv(
        bigram_freqs_no_overlap, alphabet, output_prefix.with_name(f"{output_prefix.name}_bigram_matrix_non_overlapping.csv")
    )

    h1 = calculate_h1_entropy(letter_freqs)
    h2_overlap = calculate_h2_entropy(letter_freqs, bigram_freqs_overlap)
    h2_no_overlap = calculate_h2_entropy(letter_freqs, bigram_freqs_no_overlap)

    summary_data = {
        "Parameter": ["H1 (letters)", "H2 (overlapping bigrams)", "H2 (non-overlapping bigrams)"],
        "Value": [h1, h2_overlap, h2_no_overlap]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_filepath = output_prefix.with_name(f"{output_prefix.name}_summary.csv")
    summary_df.to_csv(summary_filepath, index=False, float_format='%.6f')
    
    print(f"Зведені результати збережено у: {summary_filepath}")
    print("\n Зведені результати ")
    print(summary_df.to_string(index=False))

def main():
    input_filepath = Path('F:\sem5\crypt\Gogol_Taras.txt')
    output_dir = Path('lab1_results')
    output_dir.mkdir(exist_ok=True)
    
    # Експеримент 1: Аналіз тексту з пробілами
    text_with_spaces = prepare_text(input_filepath, keep_spaces=True)
    if text_with_spaces:
        alphabet_with_space = RUSSIAN_ALPHABET + ' '
        run_analysis(text_with_spaces, alphabet_with_space, output_dir / 'with_spaces')

    # Експеримент 2: Аналіз тексту без пробілів
    text_no_spaces = prepare_text(input_filepath, keep_spaces=False)
    if text_no_spaces:
        run_analysis(text_no_spaces, RUSSIAN_ALPHABET, output_dir / 'no_spaces')

    print(f"\nРоботу завершено. Всі результати збережено у папку '{output_dir}'.")

if __name__ == "__main__":
    main()