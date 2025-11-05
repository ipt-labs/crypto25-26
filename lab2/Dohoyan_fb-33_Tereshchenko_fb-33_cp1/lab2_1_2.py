import re
import matplotlib.pyplot as plt

RU_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def preprocess_text(raw_text: str) -> str:
    txt = raw_text.lower().replace("ё", "е")
    txt = re.sub(r"[^а-я ]", "", txt)
    return txt.replace(" ", "")

def vigenere_cipher(plain_text: str, key: str) -> str:
    result = []
    k_len = len(key)
    for i, ch in enumerate(plain_text):
        if ch in RU_ALPHABET:
            shift = (RU_ALPHABET.index(ch) + RU_ALPHABET.index(key[i % k_len])) % len(RU_ALPHABET)
            result.append(RU_ALPHABET[shift])
        else:
            result.append(ch)
    return "".join(result)

def coincidence_index(text: str) -> float:
    n = len(text)
    counts = {c: text.count(c) for c in set(text)}
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1)) if n > 1 else 0

def save_to_file(path: str, clean_text: str, encrypted: list, keys: list):
    with open(path, "w", encoding="utf-8") as f:
        f.write("=== Початковий текст ===\n")
        f.write(clean_text + "\n\n")
        f.write("=== Результати шифрування ===\n")
        f.write("=" * 120 + "\n")
        for k, enc in zip(keys, encrypted):
            f.write(f"\nКлюч: {k} (довжина {len(k)})\n")
            f.write(f"Зашифрований текст: {enc}\n")
            f.write("-" * 120 + "\n")

def visualize_indexes(keys, indexes):
    lengths = [len(k) for k in keys]
    plt.figure(figsize=(9, 5))
    plt.bar(lengths, indexes, color="skyblue", edgecolor="black")
    plt.title("Індекс відповідності залежно від довжини ключа")
    plt.xlabel("Довжина ключа")
    plt.ylabel("Індекс відповідності")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.show()

def main(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    clean = preprocess_text(text)

    keys = [
        "да",
        "чай",
        "пиво",
        "водка",
        "алкоголизм",
        "пивоварение",
        "молокопровод",
        "грабительство",
        "забинтовавшись",
        "безответственно",
        "уничижительность",
        "алкоголизовавшись",
        "умиротворительница",
        "фтизиопульмонология",
        "витаминопрофилактика"
    ]

    encrypted_texts, idxs = [], []

    for key in keys:
        enc = vigenere_cipher(clean, key)
        encrypted_texts.append(enc)
        idxs.append(coincidence_index(enc))
        print(f"\nКлюч: {key} (довжина {len(key)})")
        print(f"Зашифрований текст: {enc}")
        print("-" * 100)

    print("\nІндекс відповідності відкритого тексту:", f"{coincidence_index(clean):.6f}")
    print("\n{:<25} {:<15} {:<20}".format("Ключ", "Довжина", "Індекс відповідності"))
    print("-" * 70)
    for k, idx in zip(keys, idxs):
        print(f"{k:<25} {len(k):<15} {idx:.6f}")

    save_to_file("результати_шифрування.txt", clean, encrypted_texts, keys)
    visualize_indexes(keys, idxs)

if __name__ == "__main__":
    main("text.txt")
