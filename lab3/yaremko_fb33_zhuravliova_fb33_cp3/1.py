from collections import Counter

alphabet = set('абвгдежзийклмнопрстуфхцчшщыьэюя')

def prepare_text(text):
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')
    return ''.join(ch for ch in text if ch in alphabet)

def count_bigrams(text):
    return Counter(text[i:i+2] for i in range(0, len(text) - 1, 2))

def top5_bigrams_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned = prepare_text(raw)
    bigram_counts = count_bigrams(cleaned)
    total = sum(bigram_counts.values())

    print(f"Довжина очищеного тексту: {len(cleaned)} символів")
    print(f"Кількість неперекривних біграм: {total}")
    print("\nТоп-5:")

    for bg, cnt in bigram_counts.most_common(5):
        freq = cnt / total if total else 0
        print(f"{bg} — {cnt} разів ({freq:.4%})")

    return bigram_counts

if __name__ == "__main__":
    path = "03.txt"
    top5_bigrams_from_file(path)