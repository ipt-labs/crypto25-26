import re
from collections import Counter
import pandas as pd

def read_file(path):
    with open(path, "r", encoding="utf-8") as file:
        content = file.read().lower()
    content = content.replace("ё", "е")
    content = re.sub(r"[^а-я]", "", content)
    return content


def coincidence_index(txt, period):
    fragments = ["".join(txt[j::period]) for j in range(period)]
    ic_scores = []

    for frag in fragments:
        counter = Counter(frag)
        n = len(frag)
        ic_val = sum(c * (c - 1) for c in counter.values()) / (n * (n - 1)) if n > 1 else 0
        ic_scores.append(ic_val)

    return sum(ic_scores) / len(ic_scores)


def estimate_key_length(txt, limit=30):
    ic_data = []
    for step in range(2, limit + 1):
        ic_val = coincidence_index(txt, step)
        ic_data.append((step, ic_val))

    df = pd.DataFrame(ic_data, columns=["Довжина ключа", "IC"])
    print(df)

    probable_length = df.loc[df["IC"].idxmax(), "Довжина ключа"]
    print(f"\nЙмовірна довжина ключа: {probable_length}")
    return probable_length


def vigenere_decode(ciphertext, key_word, alphabet):
    decoded_text = []
    key_word = key_word.lower()
    k_len = len(key_word)
    k_i = 0

    for symbol in ciphertext:
        if symbol in alphabet:
            s_pos = alphabet.index(symbol)
            k_pos = alphabet.index(key_word[k_i % k_len])
            decoded_text.append(alphabet[(s_pos - k_pos) % len(alphabet)])
            k_i += 1
        else:
            decoded_text.append(symbol)

    return "".join(decoded_text)


def analyze_frequencies(ciphertext, k_len, alphabet, lang_freq):
    found_key = ""

    for j in range(k_len):
        section = ciphertext[j::k_len]
        optimal_shift = 0
        max_corr = -1

        for shift in range(len(alphabet)):
            shifted_txt = "".join(alphabet[(alphabet.index(c) - shift) % len(alphabet)] for c in section)
            counter = Counter(shifted_txt)
            total = len(section)
            corr_val = sum((counter[ch] / total) * lang_freq.get(ch, 0) for ch in alphabet)

            if corr_val > max_corr:
                max_corr = corr_val
                optimal_shift = shift

        found_key += alphabet[optimal_shift]

    print(f"\nЗнайдений ключ: {found_key.upper()}")
    return found_key


alphabet = [chr(x) for x in range(ord("а"), ord("я") + 1)]

russian_freq = {
    'а': 0.080, 'б': 0.015, 'в': 0.045, 'г': 0.017, 'д': 0.030, 'е': 0.085,
    'ж': 0.010, 'з': 0.016, 'и': 0.065, 'й': 0.010, 'к': 0.035, 'л': 0.045,
    'м': 0.030, 'н': 0.070, 'о': 0.110, 'п': 0.030, 'р': 0.050, 'с': 0.055,
    'т': 0.065, 'у': 0.025, 'ф': 0.002, 'х': 0.009, 'ц': 0.004, 'ч': 0.012,
    'ш': 0.007, 'щ': 0.003, 'ъ': 0.014, 'ы': 0.016, 'ь': 0.014, 'э': 0.003,
    'ю': 0.006, 'я': 0.018
}

ciphertext = read_file("var4.txt")
key_len = estimate_key_length(ciphertext)
detected_key = analyze_frequencies(ciphertext, key_len, alphabet, russian_freq)
plain_text = vigenere_decode(ciphertext, detected_key, alphabet)

with open("decrypted.txt", "w", encoding="utf-8") as output:
    output.write(plain_text)

print("\nРозшифрований текст збережено у файлі decrypted.txt")
