from collections import Counter
from itertools import permutations, product

alphabet = 'абвгдежзийклмнопрстуфхцчшщьыэюя'

# V3.txt
# alphabet = 'абвгдежзийклмнопрстуфхцчшщыьэюя'
M = len(alphabet) # 31
M_2 = M * M  # 961
ciphertext_path = "03.txt"

# Еталонні біграми (Відкритий текст X) та Біграми шифртексту (Шифртекст Y)
x_candidates = ['ст', 'но', 'то', 'на', 'ен']
y_candidates = ['тд', 'рб', 'во', 'щю', 'кд']

# V3.txt
# y_candidates = ['ыв', 'хр', 'хф', 'йз', 'ыя']

# Еталонні частоти літер для російської мови (у відсотках)
# Взято з комп'ютерного практикуму 1
rus_freq = {
    # Часті літери
    'о': 11.42, 'е': 8.76, 'а': 7.90,
    # Рідкісні літери
    'ф': 0.14, 'щ': 0.32, 'ь': 2.20,
}

def extended_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    d, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return (d, x, y)

def mod_inverse(a, m):
    d, x, y = extended_gcd(a, m)
    if d != 1:
        return None
    return x % m

def solve_linear_congruence(a, b, m):
    a = a % m
    b = b % m
    d, x0, y0 = extended_gcd(a, m)
    
    if b % d != 0:
        return []
    
    x_particular = (x0 * (b // d)) % m
    
    solutions = []
    m_prime = m // d
    for k in range(d):
        solution = (x_particular + k * m_prime) % m
        solutions.append(solution)
        
    return solutions

def letter_to_int(letter):
    return alphabet.find(letter)

def bigram_to_int(bigram):
    if len(bigram) != 2: return -1
    return letter_to_int(bigram[0]) * M + letter_to_int(bigram[1])

def int_to_bigram(val):
    val = val % M_2
    l1_int = val // M
    l2_int = val % M
    return alphabet[l1_int] + alphabet[l2_int]

def prepare_text(text):
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')
    return ''.join(ch for ch in text if ch in alphabet)

def load_and_prepare_ciphertext(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
        return prepare_text(raw)
    except FileNotFoundError:
        print(f"Помилка: Файл не знайдено за шляхом: {filepath}")
        return None
    except Exception as e:
        print(f"Помилка під час читання файлу: {e}")
        return None

def find_key_candidates(X_candidates, Y_candidates):
    found_keys = set()
    
    for ((X1, X2), (Y1, Y2)) in product(permutations(X_candidates, 2), permutations(Y_candidates, 2)):
        X1_int, X2_int = bigram_to_int(X1), bigram_to_int(X2)
        Y1_int, Y2_int = bigram_to_int(Y1), bigram_to_int(Y2)

        if X1_int == X2_int or Y1_int == Y2_int: continue
            
        A = (X1_int - X2_int) % M_2
        B = (Y1_int - Y2_int) % M_2
        
        a_solutions = solve_linear_congruence(A, B, M_2)
        
        for a_candidate in a_solutions:
            if a_candidate % M == 0:
                continue 

            b_candidate = (Y1_int - a_candidate * X1_int) % M_2
            found_keys.add((a_candidate, b_candidate))
            
    return sorted(list(found_keys))

def decrypt_text(ciphertext, a, b):
    a_inv = mod_inverse(a, M_2)
    
    if a_inv is None:
        return None

    plaintext = []
    for i in range(0, len(ciphertext) - 1, 2):
        bigram = ciphertext[i:i+2]
        
        if len(bigram) < 2: break
        
        Y = bigram_to_int(bigram)
        X = (a_inv * (Y - b)) % M_2        
        plaintext.append(int_to_bigram(X))
        
    return "".join(plaintext)

def is_meaningful_text(text, freq_bounds, rare_bounds):
    if not text: return False
    
    text_len = len(text)
    letter_counts = Counter(text)
    
    # Критерій 1: частота частих літер ('о', 'е', 'а')
    frequent_letters = ['о', 'е', 'а']
    current_freq_sum = sum(letter_counts.get(ch, 0) / text_len * 100 for ch in frequent_letters)
    
    lower_frequent, upper_frequent = freq_bounds
    if not (lower_frequent <= current_freq_sum <= upper_frequent):
        return False

    # Критерій 2: частота рідкісних літер ('ф', 'щ', 'ь')
    rare_letters = ['ф', 'щ', 'ь']
    current_rare_sum = sum(letter_counts.get(ch, 0) / text_len * 100 for ch in rare_letters)
    
    lower_rare, upper_rare = rare_bounds
    if not (lower_rare <= current_rare_sum <= upper_rare):
        return False
    
    return True

if __name__ == "__main__":
    error_margin = 0.30
    
    target_sum_frequent = sum(rus_freq[ch] for ch in ['о', 'е', 'а'])
    target_sum_rare = sum(rus_freq[ch] for ch in ['ф', 'щ', 'ь'])
    
    freq_bounds = (target_sum_frequent * (1 - error_margin), target_sum_frequent * (1 + error_margin))
    rare_bounds = (target_sum_rare * (1 - error_margin), target_sum_rare * (1 + error_margin))
    
    ciphertext = load_and_prepare_ciphertext(ciphertext_path)
    if ciphertext is None:
        exit()

    key_candidates = find_key_candidates(x_candidates, y_candidates)
    
    print(f"Криптоаналіз афінної біграмної підстановки (Модуль {M_2})")
    print(f"Знайдено {len(key_candidates)} унікальних кандидатів на ключ (a, b).")
    
    found_solution = False
    for i, (a, b) in enumerate(key_candidates):
        print(f" - Тестування ключа {i+1:>4}/{len(key_candidates)}: a={a:<4}, b={b:<4}")
        plaintext = decrypt_text(ciphertext, a, b)
        if plaintext is None: continue
        if is_meaningful_text(plaintext, freq_bounds, rare_bounds):
            print(f"\nЗНАЙДЕНО ВІРНИЙ КЛЮЧ: a = {a}, b = {b}")
            print("\nДешифрований текст:")
            print(plaintext)
            found_solution = True
            break
        
    if not found_solution:
        print("\n ! Жоден із перевірених кандидатів на ключ не дав змістовного тексту.")