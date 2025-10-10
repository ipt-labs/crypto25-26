import math
import pandas as pd
from collections import Counter

def clean_text(text, with_spaces=True):
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
    text = text.lower()
    text = "".join(ch for ch in text if ch in alphabet)
    if not with_spaces:
        text = text.replace(" ", "")
    return text

def letter_frequencies(text):
    total = len(text)
    counter = Counter(text)
    return {ch: counter[ch] / total for ch in sorted(counter)}

def bigram_frequencies(text, overlap=True):
    step = 1 if overlap else 2
    bigrams = [text[i:i+2] for i in range(0, len(text)-1, step)]
    total = len(bigrams)
    counter = Counter(bigrams)
    return {bg: counter[bg]/total for bg in counter}

def entropy(freqs):
    return -sum(p * math.log2(p) for p in freqs.values() if p > 0)

def entropy_bigrams(freqs):
    return entropy(freqs)/2

def redundancy(H, H0):
    return 1 - H / H0

def bigram_matrix(freqs):
    letters = sorted(set("".join(freqs.keys())))
    df = pd.DataFrame(0.0, index=letters, columns=letters)
    for bg, p in freqs.items():
        df.loc[bg[0], bg[1]] = round(p, 4)
    return df

def analyze_text(text, with_spaces=True):
    text = clean_text(text, with_spaces)

    # Частоти літер
    letter_freq = letter_frequencies(text)
    H1 = entropy(letter_freq)

    # Розмір алфавіту та H0 = log2(m)
    alphabet = set("".join(letter_freq.keys()))
    H0 = math.log2(len(alphabet))

    # Надлишковість R1
    R1 = redundancy(H1, H0)

    # Біграми
    bigram_overlap = bigram_frequencies(text, overlap=True)
    bigram_nonoverlap = bigram_frequencies(text, overlap=False)

    # Ентропія біграм (на 1 символ)
    H2_overlap = entropy_bigrams(bigram_overlap)
    H2_nonoverlap = entropy_bigrams(bigram_nonoverlap)

    # Надлишковість для біграм (відносно H0)
    R2_overlap = redundancy(H2_overlap, H0)
    R2_nonoverlap = redundancy(H2_nonoverlap, H0)

    return {
        "letters": letter_freq,
        "bigrams_overlap": bigram_overlap,
        "bigrams_nonoverlap": bigram_nonoverlap,
        "H1": H1, "R1": R1,
        "H2_overlap": H2_overlap, "R2_overlap": R2_overlap,
        "H2_nonoverlap": H2_nonoverlap, "R2_nonoverlap": R2_nonoverlap
    }

with open("Bulgakov_Mihail_Master_i_Margarita.txt", encoding="utf-8") as f:
    text = f.read()

res_spaces = analyze_text(text, with_spaces=True)
res_nospaces = analyze_text(text, with_spaces=False)

with pd.ExcelWriter("crypto_analysis.xlsx") as writer:
    
    pd.DataFrame(list(res_spaces["letters"].items()), columns=["Літера", "Частота"]) \
        .to_excel(writer, sheet_name="Letters_Spaces", index=False)
    pd.DataFrame(list(res_nospaces["letters"].items()), columns=["Літера", "Частота"]) \
        .to_excel(writer, sheet_name="Letters_NoSpaces", index=False)

    
    bigram_matrix(res_spaces["bigrams_overlap"]).to_excel(writer, sheet_name="Bigrams_Ov_Spaces")
    bigram_matrix(res_spaces["bigrams_nonoverlap"]).to_excel(writer, sheet_name="Bigrams_NonOv_Spaces")
    bigram_matrix(res_nospaces["bigrams_overlap"]).to_excel(writer, sheet_name="Bigrams_Ov_NoSpaces")
    bigram_matrix(res_nospaces["bigrams_nonoverlap"]).to_excel(writer, sheet_name="Bigrams_NonOv_NoSpaces")

    summary = pd.DataFrame({
        "Метрика": ["H1", "R1", "H2_Перетин", "R2_Перетин", "H2_Без_Перетин", "R2_Без_Перетин"],
        "З пробілами": [
            round(res_spaces["H1"], 5), round(res_spaces["R1"], 5),
            round(res_spaces["H2_overlap"], 5), round(res_spaces["R2_overlap"], 5),
            round(res_spaces["H2_nonoverlap"], 5), round(res_spaces["R2_nonoverlap"], 5)
        ],
        "Без пробілів": [
            round(res_nospaces["H1"], 5), round(res_nospaces["R1"], 5),
            round(res_nospaces["H2_overlap"], 5), round(res_nospaces["R2_overlap"], 5),
            round(res_nospaces["H2_nonoverlap"], 5), round(res_nospaces["R2_nonoverlap"], 5)
        ]
    })
    summary.to_excel(writer, sheet_name="Summary", index=False)

print("Result saved to crypto_analysis.xlsx")