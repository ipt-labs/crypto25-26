import math
import pandas as pd
from collections import Counter

alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"

def prepare_text(text: str) -> str:
    text = text.lower()
    text = text.replace("ё", "е").replace("ъ", "ь")
    return "".join([c for c in text if c in alphabet or c == " "])

def monogram_frequencies(text: str, include_spaces: bool=True):
    if not include_spaces:
        text = text.replace(" ", "")
    counts = Counter(text)
    total = sum(counts.values())
    freqs = {c: counts[c]/total for c in counts}
    return counts, freqs, total

def bigram_frequencies_step(text: str, step: int = 1, include_spaces: bool=True):
    if not include_spaces:
        text = text.replace(" ", "")
    bigrams = [text[i:i+2] for i in range(0, len(text)-1, step)]
    counts = Counter(bigrams)
    total = sum(counts.values())
    freqs = {bg: counts[bg]/total for bg in counts}
    return counts, freqs, total

def entropy(freqs: dict, n: int=1) -> float:
    H = 0
    for p in freqs.values():
        if p > 0:
            H -= p * math.log2(p)
    return H / n

def redundancy(H: float, alphabet_size: int) -> float:
    return 1 - H / math.log2(alphabet_size)

if __name__ == "__main__":
    with open("avidreaders.ru__prestuplenie-i-nakazanie-dr-izd.txt", "r", encoding="utf-8") as f:
        text = f.read()

    text = prepare_text(text)

    # монограми
    mg_counts, mg_freqs, total_mg = monogram_frequencies(text, include_spaces=True)
    H1 = entropy(mg_freqs, 1)
    R1 = redundancy(H1, len(alphabet)+1)  # +1 бо є пробіл

    mg_counts_ns, mg_freqs_ns, _ = monogram_frequencies(text, include_spaces=False)
    H1_ns = entropy(mg_freqs_ns, 1)
    R1_ns = redundancy(H1_ns, len(alphabet))

    # біграми з різними кроками
    # step=1 → перетин
    # step=2 → без перетину

    # з пробілами
    bg_counts_overlap, bg_freqs_overlap, _ = bigram_frequencies_step(text, step=1, include_spaces=True)
    H2_overlap = entropy(bg_freqs_overlap, 2)
    R2_overlap = redundancy(H2_overlap, len(alphabet)+1)

    bg_counts_no_overlap, bg_freqs_no_overlap, _ = bigram_frequencies_step(text, step=2, include_spaces=True)
    H2_no_overlap = entropy(bg_freqs_no_overlap, 2)
    R2_no_overlap = redundancy(H2_no_overlap, len(alphabet)+1)

    # без пробілів
    bg_counts_overlap_ns, bg_freqs_overlap_ns, _ = bigram_frequencies_step(text, step=1, include_spaces=False)
    H2_overlap_ns = entropy(bg_freqs_overlap_ns, 2)
    R2_overlap_ns = redundancy(H2_overlap_ns, len(alphabet))

    bg_counts_no_overlap_ns, bg_freqs_no_overlap_ns, _ = bigram_frequencies_step(text, step=2, include_spaces=False)
    H2_no_overlap_ns = entropy(bg_freqs_no_overlap_ns, 2)
    R2_no_overlap_ns = redundancy(H2_no_overlap_ns, len(alphabet))

    # Вивід
    print("Монограми з пробілами:")
    print(f"H1 = {H1:.4f}, Надлишковість = {R1:.4f}")
    print("Монограми без пробілів:")
    print(f"H1 = {H1_ns:.4f}, Надлишковість = {R1_ns:.4f}")

    print("\nБіграми з пересуванням (перетин) з пробілами:")
    print(f"H2 = {H2_overlap:.4f}, Надлишковість = {R2_overlap:.4f}")
    print("Біграми без пересування (кожні дві літери) з пробілами:")
    print(f"H2 = {H2_no_overlap:.4f}, Надлишковість = {R2_no_overlap:.4f}")
    print("Біграми з пересуванням (перетин) без пробілів:")
    print(f"H2 = {H2_overlap_ns:.4f}, Надлишковість = {R2_overlap_ns:.4f}")
    print("Біграми без пересування (кожні дві літери) без пробілів:")
    print(f"H2 = {H2_no_overlap_ns:.4f}, Надлишковість = {R2_no_overlap_ns:.4f}")

    # Збереження у Excel
    with pd.ExcelWriter("stats.xlsx") as writer:
        pd.DataFrame(mg_counts.items(), columns=["Letter", "Count"]).to_excel(writer, "Monograms", index=False)
        pd.DataFrame(mg_counts_ns.items(), columns=["Letter", "Count"]).to_excel(writer, "Monograms_no_space", index=False)

        pd.DataFrame(bg_counts_overlap.items(), columns=["Bigram", "Count"]).to_excel(writer, "Bigrams_overlap", index=False)
        pd.DataFrame(bg_counts_no_overlap.items(), columns=["Bigram", "Count"]).to_excel(writer, "Bigrams_no_overlap", index=False)

        pd.DataFrame(bg_counts_overlap_ns.items(), columns=["Bigram", "Count"]).to_excel(writer, "Bigrams_overlap_no_space", index=False)
        pd.DataFrame(bg_counts_no_overlap_ns.items(), columns=["Bigram", "Count"]).to_excel(writer, "Bigrams_no_overlap_no_space", index=False)

# Розмір алфавіту (якщо брали російські букви + пробіл)
m = 34
H0 = math.log2(m)

# Інтервали для H(n)
data = {
    10: (1.78735178991507, 2.57211724742366),
    20: (1.55396051779127, 2.26847939084822),
    30: (1.43418650606007, 2.03380418299189)
}

print(f"Максимальна ентропія H0 = {H0:.4f} біт\n")

print("n\tH(n)_avg\tR(n)")
for n, (h_min, h_max) in data.items():
    Hn = (h_min + h_max) / 2  # середнє значення
    Rn = 1 - Hn / H0
    print(f"{n}\t{Hn:.4f}\t\t{Rn:.4f}")


