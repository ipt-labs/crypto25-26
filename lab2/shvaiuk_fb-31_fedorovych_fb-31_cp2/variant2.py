from collections import Counter
import pandas as pd

alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
m = len(alphabet)

rus_freq = {
    'о': 0.1097, 'е': 0.0845, 'а': 0.0801, 'и': 0.0735, 'н': 0.0670, 'т': 0.0626,
    'с': 0.0547, 'р': 0.0473, 'в': 0.0454, 'л': 0.0440, 'к': 0.0349, 'м': 0.0321,
    'д': 0.0298, 'п': 0.0281, 'у': 0.0262, 'я': 0.0201, 'ы': 0.0190, 'ь': 0.0174,
    'г': 0.0170, 'з': 0.0165, 'б': 0.0159, 'ч': 0.0144, 'й': 0.0121, 'х': 0.0097,
    'ж': 0.0094, 'ш': 0.0073, 'ю': 0.0064, 'ц': 0.0048, 'щ': 0.0036, 'э': 0.0032,
    'ф': 0.0026, 'ъ': 0.0004
}

def load_text(file_name):
    text = open(file_name, 'r', encoding='utf-8').read().lower().replace('ё', 'е')
    return ''.join([ch for ch in text if ch in alphabet])

def compute_ic(text):
    n = len(text)
    return sum(f * (f - 1) for f in Counter(text).values()) / (n * (n - 1)) if n > 1 else 0

def divide_into_blocks(text, key_len):
    return [''.join(text[i::key_len]) for i in range(key_len)]

def calculate_avg_ic(text, max_length=30):
    data = [
        {"Key length": l, "Average IC": round(sum(compute_ic(b) for b in divide_into_blocks(text, l)) / l, 3)}
        for l in range(2, max_length + 1)
    ]
    return pd.DataFrame(data)

def find_key(text, key_len):
    key = []
    blocks = divide_into_blocks(text, key_len)
    for block in blocks:
        best_shift = min(range(m),
                         key=lambda s: sum(((Counter(block).get(alphabet[(i + s) % m], 0) / len(block)) - rus_freq.get(
                             alphabet[i], 0)) ** 2
                                           for i in range(m)))
        key.append(alphabet[best_shift])
    return ''.join(key)

def decrypt_vigenere(text, key):
    return ''.join(alphabet[(alphabet.index(c) - alphabet.index(key[i % len(key)])) % m]
                   for i, c in enumerate(text))

def main():
    file_name = "variant2.txt"
    text = load_text(file_name)
    ic_df = calculate_avg_ic(text)
    print(ic_df)
    key_len = int(ic_df.loc[ic_df["Average IC"].idxmax()]["Key length"])
    print(f"\nНайбільш ймовірна довжина ключа: {key_len}")
    key = find_key(text, key_len)
    print(f'Знайдений ключ: {key}')
    decrypted = decrypt_vigenere(text, key)
    with open('decrypted.txt', 'w', encoding='utf-8') as f:
        f.write(decrypted)
    print("Розшифрований текст збережено в decrypted.txt")

if __name__ == "__main__":
    main()
