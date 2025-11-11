import collections
import itertools
import re

VERBOSE_MODE = False

ALPHABET = "абвгдежзийклмнопрстуфхцчшщьыэюя"
M = len(ALPHABET)
M_SQUARED = M * M

MOST_COMMON_BIGRAMS_RU = ['ст', 'но', 'то', 'на', 'ен']

def preprocess_text(raw_text, alphabet):
    text = raw_text.lower()
    filtered_chars = [char for char in text if char in alphabet]
    return "".join(filtered_chars)

def find_top_bigrams(text, n=5):
    bigrams = [text[i:i+2] for i in range(0, len(text) - 1, 2)]
    bigram_counts = collections.Counter(bigrams)
    top_bigrams = [item[0] for item in bigram_counts.most_common(n)]
    return top_bigrams

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    d, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return d, x, y

def mod_inverse(a, m):
    d, x, y = extended_gcd(a, m)
    if d != 1: return None
    return x % m

def solve_linear_congruence(a, b, n):
    a, b = a % n, b % n
    d, _, _ = extended_gcd(a, n)
    if b % d != 0: return []
    a_p, b_p, n_p = a // d, b // d, n // d
    inv_a_p = mod_inverse(a_p, n_p)
    x0 = (b_p * inv_a_p) % n_p
    return [x0 + i * n_p for i in range(d)]

def text_to_bigram_numbers(text, alphabet, m):
    char_to_idx = {char: i for i, char in enumerate(alphabet)}
    numbers = []
    for i in range(0, len(text) - 1, 2):
        numbers.append(char_to_idx[text[i]] * m + char_to_idx[text[i+1]])
    return numbers

def numbers_to_text(numbers, alphabet, m):
    text = []
    for num in numbers:
        text.append(alphabet[num // m])
        text.append(alphabet[num % m])
    return "".join(text)

def decrypt(ciphertext_numbers, a, b, m_squared, m, alphabet):
    a_inv = mod_inverse(a, m_squared)
    if a_inv is None: return None
    decrypted_numbers = [(a_inv * (y - b)) % m_squared for y in ciphertext_numbers]
    return numbers_to_text(decrypted_numbers, alphabet, m)

def is_text_meaningful(text, common_chars=('о', 'а', 'е'), threshold=0.25):
    if not text: return False
    count = sum(text.count(char) for char in common_chars)
    return (count / len(text)) > threshold

def main():
    ciphertext_filename = "04_utf8.txt"

    try:
        with open(ciphertext_filename, 'r', encoding='utf-8') as f:
            raw_ciphertext = f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        try:
            with open(ciphertext_filename, 'r', encoding='cp1251') as f:
                raw_ciphertext = f.read()
        except Exception as e:
            print(f"Помилка: не вдалося прочитати файл '{ciphertext_filename}'. {e}")
            return

    processed_ciphertext = preprocess_text(raw_ciphertext, ALPHABET)
    top_5_ciphertext_bigrams = find_top_bigrams(processed_ciphertext, n=5)

    print("--- Криптоаналіз афінного біграмного шифру ---")
    print(f"Алфавіт: '{ALPHABET}' (m={M}, m²={M_SQUARED})")
    print("\nНайчастіші біграми в російській мові:", MOST_COMMON_BIGRAMS_RU)
    print("Найчастіші біграми в шифротексті:", top_5_ciphertext_bigrams)
    print("-" * 50)
    
    ru_numbers = text_to_bigram_numbers("".join(MOST_COMMON_BIGRAMS_RU), ALPHABET, M)
    cipher_numbers = text_to_bigram_numbers("".join(top_5_ciphertext_bigrams), ALPHABET, M)
    ciphertext_full_numbers = text_to_bigram_numbers(processed_ciphertext, ALPHABET, M)

    plausible_keys_found = 0
    checked_keys = set()

    for ru_pair_indices in itertools.combinations(range(len(ru_numbers)), 2):
        for cipher_pair_indices in itertools.permutations(range(len(cipher_numbers)), 2):
            if VERBOSE_MODE:
                ru_bg_1 = MOST_COMMON_BIGRAMS_RU[ru_pair_indices[0]]
                ru_bg_2 = MOST_COMMON_BIGRAMS_RU[ru_pair_indices[1]]
                c_bg_1 = top_5_ciphertext_bigrams[cipher_pair_indices[0]]
                c_bg_2 = top_5_ciphertext_bigrams[cipher_pair_indices[1]]
                print(f"Тестуємо припущення: ('{ru_bg_1}', '{ru_bg_2}') -> ('{c_bg_1}', '{c_bg_2}')")

            x_star, x_star_star = ru_numbers[ru_pair_indices[0]], ru_numbers[ru_pair_indices[1]]
            y_star, y_star_star = cipher_numbers[cipher_pair_indices[0]], cipher_numbers[cipher_pair_indices[1]]
            
            delta_x = (x_star - x_star_star) % M_SQUARED
            delta_y = (y_star - y_star_star) % M_SQUARED

            candidate_as = solve_linear_congruence(delta_x, delta_y, M_SQUARED)

            if VERBOSE_MODE and candidate_as:
                 print(f"  Знайдені кандидати для 'a': {candidate_as}")
            
            for a in candidate_as:
                if a == 0: continue
                b = (y_star - a * x_star) % M_SQUARED
                
                key = (a, b)
                if key in checked_keys:
                    continue
                checked_keys.add(key)
                
                if VERBOSE_MODE:
                    print(f"    -> Перевірка ключа (a={a}, b={b})")

                decrypted_text = decrypt(ciphertext_full_numbers, a, b, M_SQUARED, M, ALPHABET)
                
                if decrypted_text and is_text_meaningful(decrypted_text):
                    plausible_keys_found += 1
                    print(f"\n--- ЙМОВІРНИЙ КЛЮЧ №{plausible_keys_found} ЗНАЙДЕНО ---")
                    print(f"Ключ: (a = {a}, b = {b})")
                    
                    print("Розшифрований текст:")
                    if VERBOSE_MODE:
                        print(f"'{decrypted_text[:120]}...'\n")
                    else:
                        print(decrypted_text)
                        print("\n" + "="*50 + "\n") 


    print("=" * 50)
    if not VERBOSE_MODE:
        print(f"Усього перевірено унікальних ключів: {len(checked_keys)}.")

    if plausible_keys_found > 0:
        print(f"Пошук завершено. Знайдено {plausible_keys_found} ймовірних кандидатів у ключі.")
    else:
        print("Пошук завершено. Не вдалося знайти жодного ключа, що задовольняє критерії осмисленості.")

if __name__ == "__main__":
    main()