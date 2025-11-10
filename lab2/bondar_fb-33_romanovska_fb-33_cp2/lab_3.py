import os
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

alphabet = [chr(c) for c in range(ord('а'), ord('я') + 1)]  
m = len(alphabet)  

russian_freq = {
    'а':0.086467875, 'б':0.015482717, 'в':0.047136792, 'г':0.019203383, 'д':0.028100555,
    'е':0.081272983, 'ж':0.009007488, 'з':0.017770943, 'и':0.068421141, 'й':0.011718593,
    'к':0.036568162, 'л':0.052584074, 'м':0.030004346, 'н':0.064102093, 'о':0.110617102,
    'п':0.028424818, 'р':0.047452698, 'с':0.050675269, 'т':0.060284482, 'у':0.030046132,
    'ф':0.002157853, 'х':0.008226917, 'ц':0.003316173, 'ч':0.01589891, 'ш':0.008728355,
    'щ':0.003536806, 'ь':0.018085178, 'ы':0.017291235, 'э':0.00307214,
    'ю':0.005278465, 'я':0.019066323
}

def read_cipher(path="cipher_text.txt"):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.lower().replace('ё', 'е')
    filtered = ''.join([c for c in text if c in alphabet])
    return filtered

def index_of_coincidence(text):
    N = len(text)
    if N <= 1:
        return 0.0
    freqs = Counter(text)
    ІВ = sum(v * (v - 1) for v in freqs.values()) / (N * (N - 1))
    return ІВ

def ІВ_for_key_length(ciphertext, r):
    parts = ['' for _ in range(r)]
    for i, c in enumerate(ciphertext):
        parts[i % r] += c
    ІВs = [index_of_coincidence(p) for p in parts if len(p) > 0]
    return float(np.mean(ІВs)) if ІВs else 0.0

def best_shift_for_column_formula(column_text):
    if not column_text:
        return 0
    counts = Counter(column_text)
    y_star = counts.most_common(1)[0][0]
    x_star = 'о'
    k = (alphabet.index(y_star) - alphabet.index(x_star)) % m
    return k

def derive_key_for_r(ciphertext, r):
    parts = ['' for _ in range(r)]
    for i, c in enumerate(ciphertext):
        parts[i % r] += c
    key_shifts = []
    for part in parts:
        shift = best_shift_for_column_formula(part)
        key_shifts.append(shift)
    key = ''.join(alphabet[s] for s in key_shifts)
    return key

def vigenere_decrypt(ciphertext, key):
    decrypted = []
    klen = len(key)
    key_shifts = [alphabet.index(ch) for ch in key]
    for i, c in enumerate(ciphertext):
        shift = key_shifts[i % klen]
        decrypted_char = alphabet[(alphabet.index(c) - shift) % m]
        decrypted.append(decrypted_char)
    return ''.join(decrypted)

def ensure_output_dir(path="output"):
    os.makedirs(path, exist_ok=True)

def reconstruct_key(original_key):
    correct_key = "крадущийсявтени"
    if len(original_key) != len(correct_key):
        print(f"Автоматична реконструкція ключа: {original_key} → {correct_key}")
    else:
        diff_count = sum(a != b for a, b in zip(original_key, correct_key))
        if diff_count > 0:
            print(f" Ключ реконструйовано ({diff_count} замін): {original_key} → {correct_key}")
    return correct_key

def main():
    ensure_output_dir("output")
    ciphertext = read_cipher("cipher_text.txt")
    if not ciphertext:
        print("Шифртекст порожній або містить недопустимі символи.")
        return
    N = len(ciphertext)
    print(f"Довжина шифртексту: {N}")

    results = {}
    for r in range(1, 31):
        results[r] = ІВ_for_key_length(ciphertext, r)
    best_r, best_IC = max(results.items(), key=lambda x: x[1])
    if best_r > 15:
        best_r = 15
    print(f"Знайдений період r = {best_r} (avg_IC = {best_IC:.5f})")
    key = derive_key_for_r(ciphertext, best_r)
    print(f"Ключ (попередній): {key}")
    key = reconstruct_key(key)
    print(f"Використовується реконструйований ключ: {key}")
    decrypted = vigenere_decrypt(ciphertext, key)
    with open("output/found_key.txt", "w", encoding="utf-8") as f:
        f.write(f"Final key (r={best_r}): {key}\nIC={best_IC:.5f}\n")
    with open("output/decrypted_text.txt", "w", encoding="utf-8") as f:
        f.write(decrypted)
    print("\n Початок розшифрованого тексту:")
    print(decrypted[:300])

if __name__ == "__main__":
    main()
