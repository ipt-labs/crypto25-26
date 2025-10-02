import io
import math
from collections import Counter

alphabet = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

def normalize_text(s, keep_spaces=True):
    s = s.lower()
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    result = []

    if keep_spaces:
        s = " ".join(s.split())

    for ch in s:
        if ch in alphabet:
            result.append(ch)
        elif keep_spaces and ch == " ":
            result.append(" ")
    return "".join(result)


def count_ngrams(path, keep_spaces=True, buf_size=1024 * 1024):
    letters = Counter()
    bigrams_overlapping = Counter()
    bigrams_non_overlapping = Counter()
    total = 0
    prev_char = None
    prev_non_overlap_char = None
    is_even = True

    with io.open(path, "r", encoding="utf-8", errors="ignore") as f:
        while True:
            chunk = f.read(buf_size)
            if not chunk:
                break

            chunk = normalize_text(chunk, keep_spaces=keep_spaces)

            for ch in chunk:
                letters[ch] += 1
                total += 1

                if prev_char is not None:
                    if (prev_char in alphabet or (keep_spaces and prev_char == ' ')) and \
                            (ch in alphabet or (keep_spaces and ch == ' ')):
                        bigrams_overlapping[prev_char + ch] += 1
                prev_char = ch

                if is_even:
                    prev_non_overlap_char = ch
                    is_even = False
                else:
                    if (prev_non_overlap_char in alphabet or (keep_spaces and prev_non_overlap_char == ' ')) and \
                            (ch in alphabet or (keep_spaces and ch == ' ')):
                        bigrams_non_overlapping[prev_non_overlap_char + ch] += 1
                    is_even = True

    return letters, bigrams_overlapping, bigrams_non_overlapping, total

def count_H1(monograms, total):
    if total == 0:
        return 0.0
    return -sum((cnt / total) * math.log2(cnt / total) for cnt in monograms.values() if cnt > 0)

def count_H2(bigrams, monograms, total):
    denom = total - 1
    if denom <= 0:
        return 0.0

    H2 = 0.0
    for bg, cnt_ab in bigrams.items():
        a = bg[0]
        cnt_a = monograms.get(a, 0)
        if cnt_a == 0:
            continue

        p_b_a = cnt_ab / cnt_a

        p_ab = cnt_ab / denom

        if p_ab > 0 and p_b_a > 0:
            H2 -= p_ab * math.log2(p_b_a)
    return H2

def source_redundancy(entropy, symbols_count):
    if symbols_count <= 1:
        return 0.0
    return 1 - entropy / math.log2(symbols_count)

def save_results(path, output_file="crypto_analysis.txt", top_n=50):
    results_with_spaces = analyze_text(path, keep_spaces=True)

    results_without_spaces = analyze_text(path, keep_spaces=False)

    with open(output_file, "w", encoding="utf-8") as f:
        write(f, "З пробілами", results_with_spaces, top_n)
        f.write("\n" + "=" * 70 + "\n\n")
        write(f, "Без пробілів", results_without_spaces, top_n)

    print(f"Аналіз завершено. Результати збережено у '{output_file}'")

def analyze_text(path, keep_spaces):
    letters, bigrams_overlap, bigrams_non_overlap, total = count_ngrams(path, keep_spaces)

    if keep_spaces:
        letters_for_entropy = letters
        total_for_entropy = total
        symbols_set = alphabet.union({' '})
    else:
        letters_for_entropy = Counter({k: v for k, v in letters.items() if k in alphabet})
        total_for_entropy = sum(letters_for_entropy.values())
        symbols_set = alphabet

    H1 = count_H1(letters_for_entropy, total_for_entropy)
    H2_overlap = count_H2(bigrams_overlap, letters_for_entropy, total_for_entropy)
    H2_non_overlap = count_H2(bigrams_non_overlap, letters_for_entropy, total_for_entropy)

    R1 = source_redundancy(H1, len(symbols_set))
    R2_overlap = source_redundancy(H2_overlap, len(symbols_set))
    R2_non_overlap = source_redundancy(H2_non_overlap, len(symbols_set))

    return {
        "letters": letters_for_entropy,
        "bigrams_overlap": bigrams_overlap,
        "bigrams_non_overlap": bigrams_non_overlap,
        "total": total,
        "H1": H1,
        "H2_overlap": H2_overlap,
        "H2_non_overlap": H2_non_overlap,
        "R1": R1,
        "R2_overlap": R2_overlap,
        "R2_non_overlap": R2_non_overlap
    }

def write(f, label, results, top_n):
    f.write(f"============================================================\n")
    f.write(f"                  Аналіз тексту: {label: <20}        \n")
    f.write(f"============================================================\n\n")

    f.write(f"  Кількість символів: {results['total']}\n\n")

    f.write("  Ентропія та надмірність:\n")
    f.write(f"  H1: {results['H1']:.10f}\n")
    f.write(f"  H2 (Перетин): {results['H2_overlap']:.10f}\n")
    f.write(f"  H2 (Без перетину): {results['H2_non_overlap']:.10f}\n\n")

    f.write(f"  R1: {results['R1']:.10f}\n")
    f.write(f"  R2 (Перетин): {results['R2_overlap']:.10f}\n")
    f.write(f"  R2 (Без перетину): {results['R2_non_overlap']:.10f}\n\n")

    sorted_letters = results["letters"].most_common(top_n)
    total_letters_for_freq = sum(results["letters"].values())
    letter_freqs = [(k, v / total_letters_for_freq) for k, v in sorted_letters]

    write_table(f, "Частота букв", letter_freqs, "Символ", "Частота",
                display_func=lambda ch: ch if ch != " " else "␣")

    symbols = sorted(results["letters"].keys())

    bigram_overlap_matrix_data = {k: v / sum(results["bigrams_overlap"].values()) for k, v in
                                  results["bigrams_overlap"].items() if sum(results["bigrams_overlap"].values()) > 0}
    bigram_non_overlap_matrix_data = {k: v / sum(results["bigrams_non_overlap"].values()) for k, v in
                                      results["bigrams_non_overlap"].items() if
                                      sum(results["bigrams_non_overlap"].values()) > 0}

    write_matrix(f, "Матриця частот біграм (Перетин)", bigram_overlap_matrix_data, symbols)
    write_matrix(f, "Матриця частот біграм (Без перетину)", bigram_non_overlap_matrix_data, symbols)

def write_table(f, header, data, key_label, value_label, display_func=lambda x: x):
    col1_width = max(len(key_label), max((len(display_func(k)) for k, v in data), default=0)) + 2
    col2_width = max(len(value_label), 12) + 2

    f.write(f"  {header}\n")
    f.write("  " + "-" * (col1_width + col2_width + 3) + "\n")
    f.write(f"  | {key_label:<{col1_width - 2}} | {value_label:<{col2_width - 2}} |\n")
    f.write("  " + "-" * (col1_width + col2_width + 3) + "\n")

    for k, v in data:
        key_str = display_func(k)
        value_str = f"{v:.10f}".replace('.', ',')
        f.write(f"  | {key_str:<{col1_width - 2}} | {value_str:<{col2_width - 2}} |\n")

    f.write("  " + "-" * (col1_width + col2_width + 3) + "\n\n")

def write_matrix(f, header, bigrams_data, symbols, value_width=7):
    if not symbols:
        return

    f.write(f"\n  {header}\n\n")

    f.write("    ")
    for sym in symbols:
        f.write(f"{sym.replace(' ', '␣'): >{value_width}}")
    f.write("\n")
    f.write("  " + "-" * (4 + value_width * len(symbols)) + "\n")

    for row_sym in symbols:
        f.write(f"{row_sym.replace(' ', '␣'):<2} | ")
        for col_sym in symbols:
            bigram = row_sym + col_sym
            freq = bigrams_data.get(bigram, 0)
            freq_str = f"{freq:.4f}".replace('.', ',')
            f.write(f"{freq_str: >{value_width}}")
        f.write(" |\n")
    f.write("  " + "-" * (4 + value_width * len(symbols)) + "\n\n")

if __name__ == "__main__":
    try:
        save_results("warandpeace.txt", top_n=50)
    except FileNotFoundError:
        print(" Файл 'warandpeace.txt' не знайдено.")
