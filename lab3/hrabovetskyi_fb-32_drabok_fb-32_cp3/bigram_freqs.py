import re
import collections

ALPHABET = "абвгдежзийклмнопрстуфхцчшщьыэюя"
M = len(ALPHABET)


def preprocess(text: str) -> str:
    text = text.lower().translate(str.maketrans({"ё": "е", "ъ": "ь"}))
    text = re.sub(r"[^а-я]", "", text)
    return text

def bigram_frequencies(text: str, step: int = 1) -> dict:
    length = len(text)
    if step == 2 and length % 2 != 0:
        text = text[:-1]

    counter = collections.Counter(text[i:i + 2] for i in range(0, len(text) - 1, step))
    total = sum(counter.values())
    if total == 0:
        return {}
    return {bg: count / total for bg, count in counter.items()}

def main():
    try:
        with open("13.txt", "r", encoding="utf-8") as f:
            raw_text = "".join(f.read().split())
            text = preprocess(raw_text)

    except FileNotFoundError:
        print("Файл V13.txt не знайдено")
        return

    freqs_bigrams_non_overlap = bigram_frequencies(text, step=2)

    print("\nТоп-5 біграм шифртексту:")

    for bg, freq in sorted(freqs_bigrams_non_overlap.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"'{bg}': {freq:.5f}")


if __name__ == "__main__":
    main()