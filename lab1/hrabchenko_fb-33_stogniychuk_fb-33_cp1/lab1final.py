import math
import re
from collections import Counter

def preprocess_text(raw_text, alphabet):
    # Обробка тексту
    text = raw_text.lower().replace('ё', 'е').replace('ъ', 'ь')
    
    filtered_chars = [char if char in alphabet else ' ' for char in text]
    text = "".join(filtered_chars)
    
    processed_text = re.sub(r'\s+', ' ', text).strip()
    return processed_text

def calculate_entropy(frequencies, total_count):
    # ентропія
    entropy = 0.0
    for count in frequencies.values():
        if count > 0:
            probability = count / total_count
            entropy -= probability * math.log2(probability)
    return entropy

def analyze_text(text, alphabet, bigram_step):
    # частоти, біграми, ентропії, Н1 та Н2
    letter_counts = Counter(text)
    total_letters = len(text)
    letter_frequencies = {char: count / total_letters for char, count in letter_counts.items()}
    h1 = calculate_entropy(letter_counts, total_letters)

    bigrams = [text[i:i+2] for i in range(0, len(text) - 1, bigram_step) if len(text[i:i+2]) == 2]
    bigram_counts = Counter(bigrams)
    total_bigrams = len(bigrams)

    if total_bigrams == 0:
        return {
            'letter_frequencies': letter_frequencies,
            'bigram_frequencies': {},
            'H1': h1,
            'H2': 0.0
        }
    # h2
    bigram_frequencies = {bigram: count / total_bigrams for bigram, count in bigram_counts.items()}
    h2 = calculate_entropy(bigram_counts, total_bigrams) / 2

    return {
        'letter_frequencies': letter_frequencies,
        'bigram_frequencies': bigram_frequencies,
        'H1': h1,
        'H2': h2
    }

def print_frequency_table(frequencies):
    # частоти
    sorted_frequencies = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)
    for char, freq in sorted_frequencies:
        print(f"'{char}': {freq:.6f}")

def print_bigram_matrix(frequencies, alphabet):
    alphabet_chars = sorted(list(alphabet))
    
    header = "      " + "".join(f"{ch:>8}" for ch in alphabet_chars)
    print(header)
    print("--+" + "-" * (len(header) - 3))

    for first_char in alphabet_chars:
        row_str = f"  '{first_char}' |"
        for second_char in alphabet_chars:
            bigram = first_char + second_char
            freq = frequencies.get(bigram, 0.0)
            row_str += f"{freq:8.6f}"
        print(row_str)

def main():
    filename = 'cryptotext.txt'
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Файл не існує")
        return

    print(" Аналіз тексту з пробілами ")
    
    alphabet_with_spaces = 'абвгдежзийклмнопрстуфхцчшщыьэюя '
    processed_text_ws = preprocess_text(raw_text, alphabet_with_spaces)

    print("\n Біграми, що перетинаються (крок 1) ")
    results_ws_overlap = analyze_text(processed_text_ws, alphabet_with_spaces, bigram_step=1)
    print(f"Значення H1: {results_ws_overlap['H1']:.4f}")
    print(f"Значення H2: {results_ws_overlap['H2']:.4f}\n")
    
    print("\n Біграми, що НЕ перетинаються (крок 2) ")
    results_ws_no_overlap = analyze_text(processed_text_ws, alphabet_with_spaces, bigram_step=2)
    print(f"Значення H1: {results_ws_no_overlap['H1']:.4f}")
    print(f"Значення H2: {results_ws_no_overlap['H2']:.4f}\n")
    
    print("\n Частоти літер (з пробілами) ")
    print_frequency_table(results_ws_overlap['letter_frequencies'])

    print("\n Матриця частот біграм (з пробілами, крок 1) ")
    print_bigram_matrix(results_ws_overlap['bigram_frequencies'], alphabet_with_spaces)
    
    print("\n Матриця частот біграм (з пробілами, крок 2) ")
    print_bigram_matrix(results_ws_no_overlap['bigram_frequencies'], alphabet_with_spaces)

    print("\n\n Аналіз тексту БЕЗ пробілів ")
    
    alphabet_no_spaces = 'абвгдежзийклмнопрстуфхцчшщыьэюя'
    processed_text_ns = preprocess_text(raw_text, alphabet_no_spaces).replace(' ', '')
    
    print("\n Біграми, що перетинаються (крок 1) ")
    results_ns_overlap = analyze_text(processed_text_ns, alphabet_no_spaces, bigram_step=1)
    print(f"Значення H1: {results_ns_overlap['H1']:.4f}")
    print(f"Значення H2: {results_ns_overlap['H2']:.4f}\n")

    print("\n Біграми, що НЕ перетинаються (крок 2) ")
    results_ns_no_overlap = analyze_text(processed_text_ns, alphabet_no_spaces, bigram_step=2)
    print(f"Значення H1: {results_ns_no_overlap['H1']:.4f}")
    print(f"Значення H2: {results_ns_no_overlap['H2']:.4f}\n")
    
    print("\n Частоти літер (без пробілів) ")
    print_frequency_table(results_ns_overlap['letter_frequencies'])

    print("\n Матриця частот біграм (без пробілів, крок 1) ")
    print_bigram_matrix(results_ns_overlap['bigram_frequencies'], alphabet_no_spaces)

    print("\n Матриця частот біграм (без пробілів, крок 2) ")
    print_bigram_matrix(results_ns_no_overlap['bigram_frequencies'], alphabet_no_spaces)

if __name__ == '__main__':
    main()