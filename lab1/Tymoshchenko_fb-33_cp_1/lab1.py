import collections     
import math            
import pandas as pd     
import os              


# очищення тексту
def prepare(filename):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read().lower()
    text = text.replace("ё", "е").replace("ъ", "ь")
    allowed = "абвгдежзийклмнопрстуфхцчшщыьэюя "
    text = "".join(ch if ch in allowed else " " for ch in text)
    while "  " in text: 
        text = text.replace("  ", " ")
    text =  text.strip()
    return text



# частота окремих літер 
def letter_frequencies(text):
    letters = [ch for ch in text if ch.isalpha() or ch == " "]  
    lettersnospace = [ch for ch in text if ch.isalpha()]  
    
    total = len(letters)                                        
    total_ns = len(lettersnospace)
    
    counter = collections.Counter(letters)    
    counter2 = collections.Counter(lettersnospace)                                    
    
    frequencies = {ch: count / total for ch, count in counter.items()}
    frequencies_ns = {ch: count / total_ns for ch, count in counter2.items()}

    frequencies = dict(sorted(frequencies.items(), key=lambda x: x[1], reverse=True))
    frequencies_ns = dict(sorted(frequencies_ns.items(), key=lambda x: x[1], reverse=True))
    
    return frequencies, frequencies_ns


# частота біграм
def bigram_frequencies(text, overlapping=True):
    letters = [ch for ch in text if ch.isalpha() or ch == " "]
    step = 1 if overlapping else 2  
    bigrams = [letters[i] + letters[i + 1] for i in range(0, len(letters) - 1, step)]
    total = len(bigrams)
    counter = collections.Counter(bigrams)
    frequencies = {bg: count / total for bg, count in counter.items()}
    return frequencies


# створення таблиці біграм
def create_bigram_table(bigram_freq):
    alphabet = sorted(set(ch for bg in bigram_freq.keys() for ch in bg))
    matrix = {first: {second: 0 for second in alphabet} for first in alphabet}
    for bg, prob in bigram_freq.items():
        first, second = bg[0], bg[1]
        matrix[first][second] = prob
    df = pd.DataFrame(matrix).T
    df = df.round(6)
    df.index.name = "Перший символ"
    return df


# H1
def entropy(probabilities):
    return -sum(p * math.log2(p) for p in probabilities.values() if p > 0)


# H2
def conditional_entropy(bigram_freq):
    H2 = 0.0
    for bg, p_xy in bigram_freq.items():
        H2 -= (p_xy * math.log2(p_xy)) / 2
    return H2


if __name__ == "__main__":
    testtext = "testtext.txt"
    text = prepare(testtext)
    os.makedirs("results", exist_ok=True)

    #З пробілами
    # з пееркриттям
    letter_freq, letter_freq_ns = letter_frequencies(text)
    bigram_freq_overlap = bigram_frequencies(text, overlapping=True)
    H1 = entropy(letter_freq)
    H2_overlap = conditional_entropy(bigram_freq_overlap)
    table_overlap = create_bigram_table(bigram_freq_overlap)
    table_overlap.to_csv("results/з_пробілами_з_перекриттям.csv", sep=";", encoding="utf-8-sig")
    #без перекриття
    bigram_freq_nonoverlap = bigram_frequencies(text, overlapping=False)
    H2_nonoverlap = conditional_entropy(bigram_freq_nonoverlap)
    table_nonoverlap = create_bigram_table(bigram_freq_nonoverlap)
    table_nonoverlap.to_csv("results/з_пробілами_без_перекриття.csv", sep=";", encoding="utf-8-sig")

    #без пробілів
    text_no_spaces = text.replace(" ", "")
    bigram_freq_ns_overlap = bigram_frequencies(text_no_spaces, overlapping=True)
    H1_ns = entropy(letter_freq_ns)
    H2_ns_overlap = conditional_entropy(bigram_freq_ns_overlap)
    table_ns_overlap = create_bigram_table(bigram_freq_ns_overlap)
    table_ns_overlap.to_csv("results/без_пробілів_з_перекриттям.csv", sep=";", encoding="utf-8-sig")

    bigram_freq_ns_nonoverlap = bigram_frequencies(text_no_spaces, overlapping=False)
    H2_ns_nonoverlap = conditional_entropy(bigram_freq_ns_nonoverlap)
    table_ns_nonoverlap = create_bigram_table(bigram_freq_ns_nonoverlap)
    table_ns_nonoverlap.to_csv("results/без_пробілів_без_перекриття.csv", sep=";", encoding="utf-8-sig")

    N_with_space = len(letter_freq)
    N_no_space = len(letter_freq_ns)

    R1 = 1 - H1 / 5
    R2_overlap = 1 - H2_overlap / 5
    R2_nonoverlap = 1 - H2_nonoverlap / 5

    R1_ns = 1 - H1_ns / math.log2(N_no_space)
    R2_ns_overlap = 1 - H2_ns_overlap / 5
    R2_ns_nonoverlap = 1 - H2_ns_nonoverlap / 5

    with open("results/entropy_results.txt", "w", encoding="utf-8") as f:
        f.write("ентропія та надлишковість\n\n")

        f.write("З пробілами:\n")
        f.write(f"H1 = {H1:.4f}\n")
        f.write(f"H2 (з перекриттям) = {H2_overlap:.4f}\n")
        f.write(f"H2 (без перекриття) = {H2_nonoverlap:.4f}\n")
        f.write(f"R1 = {R1:.4f}\n")
        f.write(f"R2 (з перекриттям) = {R2_overlap:.4f}\n")
        f.write(f"R2 (без перекриття) = {R2_nonoverlap:.4f}\n\n")

        f.write("Без пробілів:\n")
        f.write(f"H1 = {H1_ns:.4f}\n")
        f.write(f"H2 (з перекриттям) = {H2_ns_overlap:.4f}\n")
        f.write(f"H2 (без перекриття) = {H2_ns_nonoverlap:.4f}\n")
        f.write(f"R1 = {R1_ns:.4f}\n")
        f.write(f"R2 (з перекриттям) = {R2_ns_overlap:.4f}\n")
        f.write(f"R2 (без перекриття) = {R2_ns_nonoverlap:.4f}\n")

