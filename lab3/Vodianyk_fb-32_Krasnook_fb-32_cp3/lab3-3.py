import sys
import re
from typing import List, Tuple, Optional, Set
from itertools import permutations
from pathlib import Path
from collections import Counter
import math

TARGET_ALPHABET = "абвгдежзийклмнопрстуфхцчшщьыэюя"
ALPHA_LEN = len(TARGET_ALPHABET)
MODULUS = ALPHA_LEN * ALPHA_LEN

char_to_index = {char: i for i, char in enumerate(TARGET_ALPHABET)}
index_to_char = {i: char for i, char in enumerate(TARGET_ALPHABET)}

H1_THRESHOLD = 4.455
H2_THRESHOLD = 4.125

def egcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return (b, 0, 1)
    gcd, u1, v1 = egcd(b % a, a)
    u = v1 - (b // a) * u1
    v = u1
    return (gcd, u, v)

def inverse_mod(a: int, n: int) -> Optional[int]:
    gcd, u, v = egcd(a, n)
    if gcd != 1:
        return None
    return u % n

def solve_mod_equation(a: int, b: int, n: int) -> List[int]:
    a, b = a % n, b % n
    d, u, v = egcd(a, n)
    if b % d != 0:
        return [] 
    a1, b1, n1 = a // d, b // d, n // d
    a1_inv = inverse_mod(a1, n1)
    if a1_inv is None:
        return [] 
    x0 = (b1 * a1_inv) % n1
    return [x0 + i * n1 for i in range(d)]

def bigram_to_int(bigram: str) -> int:
    try:
        x1 = char_to_index[bigram[0]]
        x2 = char_to_index[bigram[1]]
        return x1 * ALPHA_LEN + x2
    except KeyError:
        raise ValueError(f"Invalid bigram: {bigram}")

def int_to_bigram(x: int) -> str:
    try:
        x1 = x // ALPHA_LEN
        x2 = x % ALPHA_LEN
        return index_to_char[x1] + index_to_char[x2]
    except KeyError:
        raise ValueError(f"Invalid number: {x}")

def decrypt(ciphertext: str, a: int, b: int) -> Optional[str]:
    a_inv = inverse_mod(a, MODULUS)
    if a_inv is None:
        return None 
    plaintext_parts = []
    for i in range(0, len(ciphertext) - 1, 2):
        bigram_y = ciphertext[i:i+2]
        try:
            y = bigram_to_int(bigram_y)
            x = (a_inv * (y - b)) % MODULUS
            plaintext_parts.append(int_to_bigram(x))
        except (ValueError, KeyError):
            continue
    return "".join(plaintext_parts)

def read_and_clean_file(filename: str) -> Optional[str]:
    filepath = Path(__file__).parent / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ciphertext = f.read()
        return "".join(char for char in ciphertext.lower() if char in TARGET_ALPHABET)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        return None

def calculate_frequencies(text: str, n: int, overlapping: bool) -> dict:
    ngrams = []
    step = 1 if overlapping else n
    for i in range(0, len(text) - n + 1, step):
        ngrams.append(text[i:i+n])
    if not ngrams:
        return {}
    counts = Counter(ngrams)
    total_ngrams = len(ngrams)
    return {ngram: count / total_ngrams for ngram, count in counts.items()}

def calculate_h(frequencies: dict) -> float:
    if not frequencies:
        return 0.0
    return -sum(p * math.log2(p) for p in frequencies.values() if p > 0)

def find_key_candidates_top5() -> Set[Tuple[int, int]]:
    
    lang_top_bigrams = [
        "ст", "но", "то", "на", "ен"
    ]
    cipher_top_bigrams = [
        "вн", "тн", "дк", "хщ", "ун"
    ]
    
    lang_top_nums = [bigram_to_int(bg) for bg in lang_top_bigrams]
    cipher_top_nums = [bigram_to_int(bg) for bg in cipher_top_bigrams]
    
    candidate_keys: Set[Tuple[int, int]] = set()

    print(f"--- Крок 3 (Top 5): Пошук кандидатів у ключі ---")
    print(f"Модуль: {MODULUS} ({ALPHA_LEN}x{ALPHA_LEN})")
    print(f"Перевіряємо {len(list(permutations(lang_top_nums, 2))) * len(list(permutations(cipher_top_nums, 2)))} комбінацій пар (20 * 20 = 400)...")

    for x_star, x_double_star in permutations(lang_top_nums, 2):
        for y_star, y_double_star in permutations(cipher_top_nums, 2):
            a_diff = (x_star - x_double_star) % MODULUS
            b_diff = (y_star - y_double_star) % MODULUS
            
            a_sols = solve_mod_equation(a_diff, b_diff, MODULUS)
            
            for a in a_sols:
                if egcd(a, MODULUS)[0] != 1:
                    continue 
                b = (y_star - (a * x_star)) % MODULUS
                candidate_keys.add((a, b))

    print(f"Знайдено {len(candidate_keys)} унікальних кандидатів у ключі.")
    return candidate_keys


def main():
    INPUT_FILE = "05 (1).txt" 
    OUTPUT_FILE = "decrypted_05.txt"
    script_dir = Path(__file__).parent

    print(f"Початок аналізу файлу: '{INPUT_FILE}'...")
    ciphertext = read_and_clean_file(INPUT_FILE)
    if not ciphertext:
        return

    candidate_keys = find_key_candidates_top5()
    
    print(f"Перебір {len(candidate_keys)} ключів з використанням ентропійного фільтру...")
    
    valid_candidates = []

    for a, b in candidate_keys:
        plaintext = decrypt(ciphertext, a, b)
        if not plaintext:
            continue
            
        h1_entropy = calculate_h(calculate_frequencies(plaintext, n=1, overlapping=True))
        
        h2_entropy = calculate_h(calculate_frequencies(plaintext, n=2, overlapping=True)) / 2
        
        if h1_entropy < H1_THRESHOLD or h2_entropy < H2_THRESHOLD:
            valid_candidates.append((h1_entropy, h2_entropy, (a, b), plaintext))
    
    if valid_candidates:
        valid_candidates.sort(key=lambda x: (x[1], x[0]))
        
        best_h1, best_h2, found_key, found_plaintext = valid_candidates[0]
        a, b = found_key

        print("\n" + "="*40)
        print(f"Успіх: Знайдено {len(valid_candidates)} потенційних кандидатів.")
        print(f"Обрано найкращий ключ: a = {a}, b = {b}")
        print(f"Метрики: H1={best_h1:.4f}, H2={best_h2:.4f}")
        
        output_path = script_dir / OUTPUT_FILE
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(found_plaintext)
            print(f"Повний розшифрований текст збережено у файл: {output_path}")
        except Exception as e:
            print(f"Помилка збереження файлу: {e}", file=sys.stderr)
            
    else:
        print("\n" + "="*40)
        print("Невдача: Жоден кандидат не пройшов ентропійний фільтр.")

if __name__ == "__main__":
    main()