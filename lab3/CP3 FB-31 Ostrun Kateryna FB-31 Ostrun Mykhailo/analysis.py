# analysis.py
import os
from itertools import combinations, product
from utils import get_top_bigrams, bigram_to_num, modulus, solve_linear_congruence, alphabet
from scoring import score_as_russian, decrypt_ciphertext

top_russian_bigrams = ['ст', 'но', 'то', 'на', 'ен']

def print_ciphertext_fragment(cleaned_ciphertext):
    print("Наш шифртекст наступний:\n")
  
    fragment = cleaned_ciphertext[:200].upper()
  
    for i in range(0, len(fragment), 50):
        print(fragment[i:i+50])

def print_top_bigrams(title, bigrams_list, is_russian=True):
    print(f"\n{title}:\n{'-' * 30}")
  
    for idx, item in enumerate(bigrams_list, 1):
        if is_russian:
            print(f"{idx}. {item}")
        else:
            bigram, frequency = item
            print(f"{idx}. {bigram} (частота: {frequency})")
    print('-' * 30 + '\n')

def generate_key_candidates(top_russian_numbers, top_cipher_numbers):
    russian_pairs = list(combinations(range(5), 2))
    cipher_pairs = list(combinations(range(5), 2))
  
    keys = set()
    for russian_pair, cipher_pair in product(russian_pairs, cipher_pairs):
        r1, r2 = russian_pair
        russian_diff = (top_russian_numbers[r1] - top_russian_numbers[r2]) % modulus
        c1, c2 = cipher_pair
        cipher_diff = (top_cipher_numbers[c1] - top_cipher_numbers[c2]) % modulus
      
        possible_a_values = solve_linear_congruence(russian_diff, cipher_diff, modulus)
      
        for a in possible_a_values:
            b = (top_cipher_numbers[c1] - a * top_russian_numbers[r1]) % modulus
            keys.add((a, b))
          
    return list(keys)

def rank_and_save(keys, cleaned_ciphertext, results_dir):
    rankings = []
    for a, b in keys:
        plaintext = decrypt_ciphertext(cleaned_ciphertext, a, b)
        if plaintext:
            score, metrics = score_as_russian(plaintext)
            rankings.append((score, a, b, plaintext, metrics))
          
    rankings.sort(reverse=True)
    with open(os.path.join(results_dir, 'rankings.txt'), 'w', encoding='utf-8') as f:
        f.write("Рангування ключів:\n" + '-' * 60 + '\n')
      
        for idx, (sc, a, b, pt, met) in enumerate(rankings, 1):
            frag = pt[:200] + '...'
            f.write(f"{idx:2d} | Оцінка: {sc:6.2f} | a: {a:4d} | b: {b:4d} | Часті: {met['common_freq_sum']:.2f} | Рідкісні: {met['rare_freq_sum']:.2f} | Перетин: {met['overlap_ratio']:.2f} | Фрагмент: {frag}\n")
    return rankings

def print_top_and_bottom(rankings):
    print("Ми починаємо розшифровку (кілька прикладів):\n\n a b відкритий текст оцінка\n----------------------------------------------------------")
  
    num_show = min(6, len(rankings))
    indices = [0, 1, 2, len(rankings)-3, len(rankings)-2, len(rankings)-1] if len(rankings) >= 6 else list(range(len(rankings)))
  
    for idx in indices[:num_show]:
        score, a, b, pt, _ = rankings[idx]
        fragment = pt[:20].upper() + '...'
        print(f"({a:<4}, {b:<4}) {fragment:<32} {score:8.2f}")

def save_candidates(keys, results_dir):
    with open(os.path.join(results_dir, 'candidates.txt'), 'w', encoding='utf-8') as f:
        f.write("Кандидати на ключі (a, b):\n" + '-' * 30 + '\n')
      
        for idx, (a, b) in enumerate(keys, 1):
            f.write(f"{idx:2d} | a: {a:4d} | b: {b:4d}\n")

def perform_analysis(cipher_file, results_dir='results'):
    os.makedirs(results_dir, exist_ok=True)
    with open(cipher_file, 'r', encoding='utf-8') as f:
        ciphertext = f.read().strip()
      
    cleaned_ciphertext = ''.join(c.lower() for c in ciphertext if c.lower() in alphabet)
    print_ciphertext_fragment(cleaned_ciphertext)
  
    top_cipher = get_top_bigrams(cleaned_ciphertext)
    print_top_bigrams("Найчастіші біграми в російській мові", top_russian_bigrams)
    print_top_bigrams("Найчастіші біграми в шифротексті", top_cipher, is_russian=False)
  
    top_ct_nums = [bigram_to_num(bg[0]) for bg in top_cipher]
    top_ru_nums = [bigram_to_num(bg) for bg in top_russian_bigrams]
  
    keys = generate_key_candidates(top_ru_nums, top_ct_nums)
    save_candidates(keys, results_dir)
  
    rankings = rank_and_save(keys, cleaned_ciphertext, results_dir)
  
    if rankings:
        print_top_and_bottom(rankings)
        best_score, best_a, best_b, best_pt, best_metrics = rankings[0]
      
        with open(os.path.join(results_dir, 'decrypted.txt'), 'w', encoding='utf-8') as f:
            f.write(best_pt)
          
        print(f"\nНайкращий ключ: a={best_a}, b={best_b}\n")
        best_fragment = best_pt[:200].upper()
      
        for i in range(0, len(best_fragment), 50):
            print(best_fragment[i:i+50])
          
        print(f"\nКількість кандидатів: {len(keys)}.")

if __name__ == "__main__":
    perform_analysis("08.txt")
