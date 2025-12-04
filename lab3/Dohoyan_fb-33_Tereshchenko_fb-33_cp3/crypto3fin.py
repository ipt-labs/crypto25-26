import sys
import re
from collections import Counter
import math

let = "абвгдежзийклмнопрстуфхцчшщьыэюя"
m = len(let)
M = m * m
letter_to_num = {letter: index for index, letter in enumerate(let)}
num_to_letter = {index: letter for index, letter in enumerate(let)}
top5_big = ["ст", "но", "то", "на", "ен"]
incorect_big = [
    'аы','оы','иы','ыы','уы','еы','юы','яы','эы',
    'аь','оь','иь','ыь','уь','еь','юь','яь','эь'
]
max_imp = 2

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a, m):
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def bigram_to_num(bg):
    return letter_to_num[bg[0]] * m + letter_to_num[bg[1]]

def num_to_bigram(num):
    return num_to_letter[num // m] + num_to_letter[num % m]

def decrypt(text, a, b):
    a_inv = mod_inverse(a, M)
    if a_inv is None:
        return ""
    plaintext = []
    if len(text) % 2 != 0:
        text = text[:-1]

    for i in range(0, len(text), 2):
        bg = text[i:i + 2]
        if bg[0] not in letter_to_num or bg[1] not in letter_to_num:
            continue
        y = bigram_to_num(bg)
        x = (a_inv * (y - b)) % M
        plaintext.append(num_to_bigram(x))
    return "".join(plaintext)

def top_bigrams(text, n=5):
    bigram = Counter()
    for i in range(0, len(text) - 1, 2):
        if text[i] in letter_to_num and text[i + 1] in letter_to_num:
            bigram[text[i:i + 2]] += 1
    top = bigram.most_common(n)
    return [bg for bg, _ in top]

def index_of_coincidence(text):
    counts = Counter(text)
    length = sum(counts.values())
    if length < 2:
        return 0
    return sum(v * (v - 1) for v in counts.values()) / (length * (length - 1))

def has_incorrectbig(text):
    for bg in incorect_big:
        if text.count(bg) > max_imp:
            return True
    return False

def solve_for_a_candidates(x1, x2, y1, y2):
    A = (x1 - x2) % M
    B = (y1 - y2) % M
    g = math.gcd(A, M)
    if B % g != 0:
        return []
    inv = mod_inverse(A, M)
    if inv is None:
        return []

    a0 = (inv * B) % M
    return [(a0 + k * M) % M for k in range(g)]
def build_key_candidates(cipher_top, lang_top):
    candidates = set()
    for i in range(len(cipher_top)):
        for j in range(len(cipher_top)):
            if i == j:
                continue
            for p in range(len(lang_top)):
                for q in range(len(lang_top)):
                    if p == q:
                        continue
                    y1 = bigram_to_num(cipher_top[i])
                    y2 = bigram_to_num(cipher_top[j])
                    x1 = bigram_to_num(lang_top[p])
                    x2 = bigram_to_num(lang_top[q])
                    a_list = solve_for_a_candidates(x1, x2, y1, y2)
                    for a in a_list:
                        if math.gcd(a, M) != 1: 
                            continue
                        b = (y1 - a * x1) % M
                        candidates.add((a, b))
    return sorted(candidates)
def clean_text(text):
    text = text.lower().replace("ё", "е").replace("ъ", "ь")
    text = "".join(ch for ch in text if ch in letter_to_num)
    if len(text) % 2 != 0:
        text = text[:-1]
    return text
def main():
    FILE_PATH = "02.txt"

    try:
        with open(FILE_PATH, encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        sys.exit(1)
    text = clean_text(text)
    print(f"Довжина тексту: {len(text)}")
    cipher_top = top_bigrams(text, n=5)
    print("Топ-5 біграм шифротексту:", cipher_top)
    candidates = build_key_candidates(cipher_top, top5_big)
    print(f"Знайдено {len(candidates)} кандидатів ключів.\n")
    valid_count = 0
    with open("decrypted_result.txt", "w", encoding="utf-8") as fout:
        for idx, (a, b) in enumerate(candidates, start=1):
            dec = decrypt(text, a, b)
            if not dec or has_incorrectbig(dec):
                continue
            ic = index_of_coincidence(dec)
            if ic < 0.045:  
                continue
            valid_count += 1
            print(f"#{valid_count}  a={a}, b={b}  IC={ic:.6f}")
            print("Початок розшифрованого тексту:")
            print(dec[:200])
            print("-" * 60)
            fout.write(f"#{valid_count}  a={a}, b={b}  IC={ic:.6f}\n")
            fout.write(dec + "\n" + "-" * 60 + "\n")
    print(f"Всього валідних кандидатів: {valid_count}")
    print("Всі валідні розшифрування збережено у 'decrypted_result.txt'")

if __name__ == "__main__":
    main()
