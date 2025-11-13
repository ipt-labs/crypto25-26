import re
from collections import Counter
from itertools import permutations

ALPHABET = "абвгдежзийклмнопрстуфхцчшщьыэюя"
m = len(ALPHABET)

def clean_text(input_path: str):
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    text = text.strip().lower().replace("ё", "е").replace("ъ", "ь")
    text = re.sub(r'[^а-я]', '', text)
    return text

def gcd(a: int, b: int):
    a0, b0 = abs(a), abs(b)
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    while b0 != 0:
        q = a0 // b0
        a0, b0, x0, x1, y0, y1 = b0, a0 - q * b0, x1, x0 - q * x1, y1, y0 - q * y1
    g = a0
    x = x0 if a >= 0 else -x0
    y = y0 if b >= 0 else -y0
    return (g, x, y)

def mod_inv(a: int, mod: int):
    g, x, _ = gcd(a, mod)
    if g != 1:
        return None
    return x % mod

def solve_linear_congruence(a: int, b: int, n: int):
    if n <= 0:
        return []
    a %= n
    b %= n
    d, _, _ = gcd(a, n)
    if b % d != 0:
        return []
    a1 = a // d
    b1 = b // d
    n1 = n // d
    inv_a1 = mod_inv(a1, n1)
    if inv_a1 is None:
        return []
    x0 = (inv_a1 * b1) % n1
    solutions = [(x0 + k * n1) % n for k in range(d)]
    return sorted(set(solutions))

def bigram_to_number(bg: str):
    return ALPHABET.index(bg[0]) * m + ALPHABET.index(bg[1])

def number_to_bigram(n: int):
    n = n % (m * m)
    return ALPHABET[n // m] + ALPHABET[n % m]

def count_bigrams(text: str):
    bigrams = [text[i]+text[i+1] for i in range(0, len(text)-1, 2) if i+1 < len(text)]
    freq = Counter(bigrams)
    total = sum(freq.values())
    top5 = [bg for bg, _ in freq.most_common(5)]
    return top5, freq

def decrypt_text(text: str, a: int, b: int):
    mod = m * m
    inv_a = mod_inv(a, mod)
    if inv_a is None:
        return None
    result = []
    for i in range(0, len(text)-1, 2):
        if i+1 >= len(text):
            break
        y = bigram_to_number(text[i]+text[i+1])
        x = (inv_a * (y - b)) % mod
        result.append(number_to_bigram(x))
    return ''.join(result)

def is_russian_text(text: str, verbose=False):
    if len(text) < 50:
        return False
    
    letters = Counter(text)
    total = len(text)
    
    common_letters = "оеаинтср"
    rare_letters = "фщъэ"
    
    common_freq = sum(letters.get(c, 0) for c in common_letters) / total
    rare_freq = sum(letters.get(c, 0) for c in rare_letters) / total
    typical_bigrams = ["ст", "но", "то", "на", "ен", "ов", "ра", "ко", "ор", "ер"]
    bigram_count = 0
    for i in range(len(text)-1):
        if text[i:i+2] in typical_bigrams:
            bigram_count += 1
    bigram_freq = bigram_count / (len(text) - 1) if len(text) > 1 else 0
    
    bad_bigrams = ["йй", "ыы", "ьь", "ъъ", "щщ", "жй", "фщ"]
    bad_count = sum(text.count(bg) for bg in bad_bigrams)
    
    if verbose:
        print(f"  Частота поширених літер: {common_freq:.3f}")
        print(f"  Частота рідкісних літер: {rare_freq:.3f}")
        print(f"  Частота типових біграм: {bigram_freq:.3f}")
        print(f"  Погані біграми: {bad_count}")
    
    return (common_freq > 0.35 and 
            rare_freq < 0.08 and 
            bigram_freq > 0.05 and 
            bad_count < len(text) * 0.01)

def find_key_and_decrypt(cipher_text, verbose=True):
    
    top5_plain = ["ст", "но", "то", "на", "ен"]
    top5_cipher, freq = count_bigrams(cipher_text)
    
    if verbose:
        print("Топ-5 біграм шифртексту:")
        for bg in top5_cipher:
            print(f"  {bg}: {freq[bg]}")
    
    mod = m * m
    results = []
    tested = 0
    
    for p1, p2 in permutations(top5_plain, 2):
        X1, X2 = bigram_to_number(p1), bigram_to_number(p2)
        
        for c1, c2 in permutations(top5_cipher, 2):
            Y1, Y2 = bigram_to_number(c1), bigram_to_number(c2)
            a_candidates = solve_linear_congruence((X1 - X2) % mod, (Y1 - Y2) % mod, mod)
            
            for a in a_candidates:
                if gcd(a, mod)[0] != 1:
                    continue
                b = (Y1 - a * X1) % mod
                tested += 1
                decrypted = decrypt_text(cipher_text, a, b)
                if decrypted is None:
                    continue       
                if verbose and tested % 1000 == 0:
                    print(f"Протестовано {tested} ключів...")
                if is_russian_text(decrypted):
                    results.append((a, b, decrypted, (p1, p2, c1, c2)))
    
    if verbose:
        print(f"\nВсього протестовано {tested} ключів")
        print(f"Знайдено {len(results)} потенційних розшифрувань")
    
    return results


cipher_text = clean_text("07.txt")
print(f"Довжина шифртексту: {len(cipher_text)} символів\n")

found = find_key_and_decrypt(cipher_text, verbose=True)

if not found:
    print("\nНе вдалося знайти ключ")
else:
    a, b, decrypted_text, mapping = found[0]  
    print(f"Знайдено правильний ключ:")
    print(f"Ключ: a={a}, b={b}")
    print(f"Відображення: {mapping[0]},{mapping[1]} -> {mapping[2]},{mapping[3]}")
    print(f"\nПочаток розшифрованого тексту:\n{decrypted_text[:500]}")  

    with open("decrypted.txt", "w", encoding="utf-8") as f:
        f.write(decrypted_text)
    print(f"\nРозшифрований текст збережено у decrypted.txt")