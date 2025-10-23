import sys
import itertools

alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"
m = len(alphabet)
M = m * m 

letter_to_index = {letter: index for index, letter in enumerate(alphabet)}

def extended_euclidean(a, b):
    if b == 0:
        return (a, 1, 0)
    gcd, x1, y1 = extended_euclidean(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return (gcd, x, y)

def mod_inverse(a, m):
    if m == 1:
        return 0
    gcd, x, y = extended_euclidean(a, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def solve_linear_congruence(A, B, N):
    A = (A % N + N) % N
    B = (B % N + N) % N
    gcd, x0, y0 = extended_euclidean(A, N)
    
    solutions = []
    if B % gcd != 0:
        return []
    else:
        A1 = A // gcd
        B1 = B // gcd
        N1 = N // gcd
        A1_inv = mod_inverse(A1, N1)
        if A1_inv is None:
             return []
        
        x_base = (A1_inv * B1) % N1
        for i in range(gcd):
            solutions.append(x_base + i * N1)
    return solutions

def bigram_to_value(bigram, m, local_letter_to_index):
    try:
        x1 = local_letter_to_index[bigram[0]]
        x2 = local_letter_to_index[bigram[1]]
        return x1*m + x2
    except KeyError:
        return None

def find_keys():
    plaintext_top_N = ['ст', 'но', 'то', 'на', 'ен']
    ciphertext_top_N = ['йа', 'юа', 'чш', 'юд', 'рщ'] 

    print(f"Алфавіт: {m} букв. Модуль M = m*m = {M}")
    print("Пошук ключів...")

    candidate_keys = set()
    index_pairs = list(itertools.combinations(range(len(plaintext_top_N)), 2))
    
    for x_idx1, x_idx2 in index_pairs:
        X1 = bigram_to_value(plaintext_top_N[x_idx1], m, letter_to_index)
        X2 = bigram_to_value(plaintext_top_N[x_idx2], m, letter_to_index)
        X_diff = (X1 - X2) % M

        for y_idx1, y_idx2 in list(itertools.permutations(range(len(ciphertext_top_N)), 2)):
            Y1 = bigram_to_value(ciphertext_top_N[y_idx1], m, letter_to_index)
            Y2 = bigram_to_value(ciphertext_top_N[y_idx2], m, letter_to_index)
            
            if Y1 is None or Y2 is None: continue
                
            Y_diff = (Y1 - Y2) % M
            
            possible_a_keys = solve_linear_congruence(X_diff, Y_diff, M)

            for a_key in possible_a_keys:
                if mod_inverse(a_key, M) is None:
                    continue
                
                b_key = (Y1 - a_key * X1) % M
                candidate_keys.add((a_key, b_key))

    print(f"Знайдено {len(candidate_keys)} ключів.")

    KEY_OUTPUT_FILE = 'keys.txt'
    try:
        with open(KEY_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for a_key, b_key in sorted(list(candidate_keys)):
                f.write(f"{a_key},{b_key}\n")
        print(f"Ключі збережені у файл '{KEY_OUTPUT_FILE}'.")
    except Exception as e:
        print(f"Помилка у '{KEY_OUTPUT_FILE}': {e}", file=sys.stderr)

if __name__ == "__main__":
    find_keys()