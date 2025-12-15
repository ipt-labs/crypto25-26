import os
import re
from collections import Counter
from itertools import permutations

FILENAME = '04.txt'
ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
M = 31
M_SQ = M * M

TARGET_FREQS = {
    'о': 0.1098, 'е': 0.0848, 'а': 0.0799, 'и': 0.0736, 
    'н': 0.0670, 'т': 0.0631, 'с': 0.0547, 'р': 0.0474
}

def gcd_extended(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = gcd_extended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a, m):
    gcd, x, _ = gcd_extended(a, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def solve_linear_congruence(a, b, n):
    gcd, x0, _ = gcd_extended(a, n)
    if b % gcd != 0:
        return []
    x0 = (x0 * (b // gcd)) % n
    solutions = []
    step = n // gcd
    for i in range(gcd):
        solutions.append((x0 + i * step) % n)
    return solutions

def get_text_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        content = content.replace('ё', 'е').replace('ъ', 'ь')
        content = re.sub(f'[^{ALPHABET}]', '', content)
        return content
    except FileNotFoundError:
        return None

def text_to_indices(text):
    return [ALPHABET.index(c) for c in text]

def indices_to_text(indices):
    return ''.join([ALPHABET[i] for i in indices])

def get_bigram_values(indices):
    bigrams = []
    for i in range(0, len(indices) - 1, 2):
        val = indices[i] * M + indices[i+1]
        bigrams.append(val)
    return bigrams

def indices_from_bigrams(bigram_values):
    indices = []
    for val in bigram_values:
        indices.extend([val // M, val % M])
    return indices

def decrypt_affine(cipher_bigrams, a, b):
    a_inv = mod_inverse(a, M_SQ)
    if a_inv is None:
        return None
    return [(a_inv * (y - b)) % M_SQ for y in cipher_bigrams]

def calculate_fitness(text_snippet):
    if not text_snippet: return float('inf')
    counts = Counter(text_snippet)
    length = len(text_snippet)
    score = 0.0
    for char, target_freq in TARGET_FREQS.items():
        actual_freq = counts[char] / length
        score += (actual_freq - target_freq) ** 2
    return score

def main():
    if not os.path.exists('results'):
        os.makedirs('results')

    raw_text = get_text_from_file(FILENAME)
    if not raw_text:
        print(f"Файл {FILENAME} не знайдено")
        return

    indices = text_to_indices(raw_text)
    cipher_bigrams = get_bigram_values(indices)
    
    ctr = Counter(cipher_bigrams)
    top_cipher_bg_vals = [k for k, v in ctr.most_common(5)]
    
    print("\nТоп-5 біграм шифртексту:")
    with open('results/top_bigrams.txt', 'w', encoding='utf-8') as f:
        f.write("Топ-5 біграм шифртексту:\n")
        for val in top_cipher_bg_vals:
            chars = ALPHABET[val // M] + ALPHABET[val % M]
            freq = ctr[val] / len(cipher_bigrams)
            line = f"'{chars}': {freq:.5f}"
            print(line)
            f.write(line + "\n")

    top_ru_strs = ["ст", "но", "то", "на", "ен"]
    top_ru_vals = [ALPHABET.index(s[0])*M + ALPHABET.index(s[1]) for s in top_ru_strs]

    print("\nКлючі кандидати:")
    candidates = set()
    
    for x1, x2 in permutations(top_ru_vals, 2):
        delta_x = (x1 - x2) % M_SQ
        for y1, y2 in permutations(top_cipher_bg_vals, 2):
            delta_y = (y1 - y2) % M_SQ
            possible_as = solve_linear_congruence(delta_x, delta_y, M_SQ)
            for a in possible_as:
                if gcd_extended(a, M)[0] != 1:
                    continue
                b = (y1 - a * x1) % M_SQ
                candidates.add((a, b))

    with open('results/key_candidates.txt', 'w', encoding='utf-8') as f:
        for a, b in candidates:
            f.write(f"{a} {b}\n")
    print(f"Знайдено {len(candidates)} кандидатів. Збережено у папку results")
    
    best_score = float('inf')
    best_key = None
    best_text_preview = ""
    full_decrypted_text = ""

    check_length = min(len(cipher_bigrams), 500)
    cipher_sample = cipher_bigrams[:check_length]

    print("Дешифрування та пошук змістовного тексту")
    
    for a, b in candidates:
        dec_sample = decrypt_affine(cipher_sample, a, b)
        if not dec_sample: continue
        
        txt_sample = indices_to_text(indices_from_bigrams(dec_sample))
        score = calculate_fitness(txt_sample)
        
        if score < best_score:
            best_score = score
            best_key = (a, b)
            best_text_preview = txt_sample
            full_indices = indices_from_bigrams(decrypt_affine(cipher_bigrams, a, b))
            full_decrypted_text = indices_to_text(full_indices)

    print("\nРезультати")
    if best_key:
        print(f"Знайдено найкращий ключ (a, b): {best_key}")
        print(f"Оцінка: {best_score:.6f} (менше=краще)")
        print(f"\nДешифрований текст:\n{best_text_preview}") 
        
        with open('results/decrypted.txt', 'w', encoding='utf-8') as f:
            f.write(full_decrypted_text)
        print("Дешифрований текст збережено у папці results")
    else:
        print("Не вдалося знайти змістовний текст")

if __name__ == "__main__":
    main()

