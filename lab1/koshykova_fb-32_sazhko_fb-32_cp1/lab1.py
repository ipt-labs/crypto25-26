import re
from collections import Counter
import pandas as pd
import math

#фільтрація і збереження тексту
def clean_text(text, keep_spaces=True):
    text = text.lower()
    text = re.sub(r'[^а-яё\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not keep_spaces:
        text = text.replace(' ', '')
    return text

def save_filtered(raw_text, path_with_spaces, path_no_spaces):
    filtered = clean_text(raw_text, keep_spaces=True)
    filtered_no_spaces = clean_text(raw_text, keep_spaces=False)

    with open(path_with_spaces, "w", encoding="utf-8") as f:
        f.write(filtered)
    with open(path_no_spaces, "w", encoding="utf-8") as f:
        f.write(filtered_no_spaces)

        return filtered, filtered_no_spaces

#частота літер
def letter_freq(text):
    counts = Counter(text)
    total = len(text)
    freqs = {c: count / total for c, count in counts.items()}
    return dict(sorted(freqs.items(), key=lambda x: x[1], reverse=True))

#частота біграм
def bigram_freq(text, step=1):
    bigrams = [text[i:i+2] for i in range(0, len(text)-1, step) if len(text[i:i+2]) == 2]
    counts = Counter(bigrams)
    total = len(bigrams)
    freqs = {bg: count / total for bg, count in counts.items()}
    return freqs

#ентропія
def entropy(freq_dict, bigram=False):
    H = -sum(p * math.log2(p) for p in freq_dict.values() if p > 0)
    if bigram:
        H /= 2
    return H

#надлишковість
def redundancy(H, max_H):
    return 1 - (H / max_H)

#збереження результатів
def save_results(letter_space, letter_nospace, bi_overlap, bi_nonoverlap, bi_overlap_nospace, bi_nonoverlap_nospace, filename, alphabet):
    with pd.ExcelWriter(filename) as writer:
        
        df_letter_space = pd.DataFrame(list(letter_space.items()), columns=['Літера', 'Частота'])
        df_letter_space.to_excel(writer, sheet_name="Букви з пробілом", index=False)
        
        df_letter_nospace = pd.DataFrame(list(letter_nospace.items()), columns=['Літера', 'Частота'])
        df_letter_nospace.to_excel(writer, sheet_name="Букви без пробілу", index=False)

        def save_bigram(freqs, sheet_name):
            matrix = pd.DataFrame(0.0, index=alphabet, columns=alphabet)
            for bg, f in freqs.items():
                matrix.at[bg[0], bg[1]] = f
            matrix.to_excel(writer, sheet_name=sheet_name)

        save_bigram(bi_overlap, "Перетинаючі біграми")
        save_bigram(bi_nonoverlap, "Неперетинаючі біграми")
        save_bigram(bi_overlap_nospace, "Оверлап біграми без пробілy")
        save_bigram(bi_nonoverlap_nospace, "Ноноверлап біграми без пробілу")

#меін процес
def main():
    file_path = 'biblia.txt'
    output_file = 'results.txt'

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    filtered, filtered_no_spaces = save_filtered(raw_text, "filtered.txt", "filtered_no_spaces.txt")

    alphabet = list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя ')

    filtered = clean_text(raw_text, keep_spaces=True)
    filtered_no_spaces = clean_text(raw_text, keep_spaces=False)

    letter_space = letter_freq(filtered)
    letter_nospace = letter_freq(filtered_no_spaces)

    bi_overlap = bigram_freq(filtered, step=1)
    bi_nonoverlap = bigram_freq(filtered, step=2)
    bi_overlap_nospace = bigram_freq(filtered_no_spaces, step=1)
    bi_nonoverlap_nospace = bigram_freq(filtered_no_spaces, step=2)

    H1_space = entropy(letter_space)
    H1_nospace = entropy(letter_nospace)
    H2_overlap = entropy(bi_overlap, bigram=True)
    H2_nonoverlap = entropy(bi_nonoverlap, bigram=True)
    H2_overlap_nospace = entropy(bi_overlap_nospace, bigram=True)
    H2_nonoverlap_nospace = entropy(bi_nonoverlap_nospace, bigram=True)

    max_H_space = math.log2(34)
    max_H_nospace = math.log2(33)

    R_space = redundancy(H1_space, max_H_space)
    R_nospace = redundancy(H1_nospace, max_H_nospace)
    R_overlap = redundancy(H2_overlap, max_H_space)
    R_nonoverlap = redundancy(H2_nonoverlap, max_H_space)
    R_overlap_nospace = redundancy(H2_overlap_nospace, max_H_nospace)
    R_nonoverlap_nospace = redundancy(H2_nonoverlap_nospace, max_H_nospace)

    lines = [
        "Ентропія\n",
        f"H1 букви з пробілом: {H1_space:.6f}\n",
        f"H1 букви без пробілу: {H1_nospace:.6f}\n",
        f"H2 перетинаючі біграми: {H2_overlap:.6f}\n",
        f"H2 перетинаючі без пробілу: {H2_overlap_nospace:.6f}\n",
        f"H2 неперетинаючі біграми: {H2_nonoverlap:.6f}\n",
        f"H2 неперетинаючі без пробілу: {H2_nonoverlap_nospace:.6f}\n\n",
        "Надлишковість\n",
        f"R букви з пробілом: {R_space:.6f}\n",
        f"R букви без пробілу: {R_nospace:.6f}\n",
        f"R перетинаючі біграми: {R_overlap:.6f}\n",
        f"R перетинаючі без пробілу: {R_overlap_nospace:.6f}\n",
        f"R неперетинаючі біграми: {R_nonoverlap:.6f}\n",
        f"R неперетинаючі без пробілу: {R_nonoverlap_nospace:.6f}\n"
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    save_results(letter_space, letter_nospace, bi_overlap, bi_nonoverlap, bi_overlap_nospace, bi_nonoverlap_nospace, "results.xlsx", alphabet)

if __name__ == "__main__":
    main()