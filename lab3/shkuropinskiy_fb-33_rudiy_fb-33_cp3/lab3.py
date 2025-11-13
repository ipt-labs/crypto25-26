import operator

alphabet = 'абвгдежзийклмнопрстуфхцчшщьыэюя'
frequent_bigrams = ['ст', 'но', 'то', 'на', 'ен']
impossible_bigrams = ['аы', 'оы', 'иы', 'ыы', 'уы', 'еы', 'аь', 'оь', 'иь', 
                      'ыь', 'уь', 'еь', 'юы', 'яы', 'эы', 'юь', 'яь', 'эь']

def clean_text(text, alphabet):
    text = text.lower()
    cleaned = ''
    for ch in text:
        if ch in alphabet:
            cleaned += ch
    return cleaned

def extended_euclid(a, b):
        if (b==0):
                return a, 1, 0
        d, u, v = extended_euclid(b, a % b)
        return d, v, u - (a // b) * v

def solve_linear_congruence(a, b, n):
        d, u, v = extended_euclid(a, n)
        solutions = []

        if b % d != 0:
            return []
        
        a1 = a // d
        b1 = b // d
        n1 = n // d

        d1, u1, v1 = extended_euclid(a1, n1)

        x = (b1 * u1) % n1

        for i in range(d):
            solutions.append(x + i * n1)
        
        return solutions


def bigrams(text, letter_russian,  step=1):
    bigrams_count = {}
    top_5_list = []

    for i in range(0, len(text) - 1, step):
        a, b = text[i], text[i + 1]
        bigram = a + b
        if bigram in bigrams_count:
            bigrams_count[bigram] += 1
        else:
            bigrams_count[bigram] = 1
        # print(bigrams_count)
    sorted_bigrams = sorted(bigrams_count.items(), key=operator.itemgetter(1), reverse=True)
    first_five_pairs = sorted_bigrams[:5]
    dict_of_bigrams = {}
    for bigram, count in first_five_pairs:
        dict_of_bigrams[bigram] = count      
    print(dict_of_bigrams)
    return list(dict_of_bigrams)

def get_bigram_id(bigram, alphabet):
    return alphabet.index(bigram[0]) * len(alphabet) + alphabet.index(bigram[1])


def generate_keys(bigrams, cipher_bigrams, alphabet):
    keys = []
    m2 = len(alphabet) ** 2
    for i in bigrams:
        for j in bigrams:
            if i == j:
                continue
            for u in cipher_bigrams:
                for v in cipher_bigrams:
                    if u == v:
                        continue

                    x1 = get_bigram_id(i, alphabet)
                    x2 = get_bigram_id(j, alphabet)
                    y1 = get_bigram_id(u, alphabet)
                    y2 = get_bigram_id(v, alphabet)

                    a = (x1 - x2) % m2
                    b = (y1 - y2) % m2

                    a_candidates = solve_linear_congruence(a, b, m2)

                    for a in a_candidates:
                        b = (y1 - a * x1) % m2
                        keys.append((a, b))
    return list(set(keys))

def decrypt_affine(cipher_text, a, b, alphabet):
    m = len(alphabet)
    m2 = m ** 2

    gcd, u, v = extended_euclid(a, m2)
    if gcd != 1:
        return None  

    a_inv = u % m2
    decrypted_text = ''

    for i in range(0, len(cipher_text) - 1, 2):
        bigram = cipher_text[i:i+2]
        if len(bigram) < 2:
            continue
        y = get_bigram_id(bigram, alphabet)
        x = (a_inv * (y - b)) % m2
        first_letter = alphabet[x // m]
        second_letter = alphabet[x % m]
        decrypted_text += first_letter + second_letter

    return decrypted_text


def is_valid_text(text, impossible_bigrams):
    for bad in impossible_bigrams:
        if bad in text:
            return False
        
    o_count = text.count('о')
    a_count = text.count('а')
    e_count = text.count('е')

    total_chars = len(text)

    if (o_count + a_count + e_count) / total_chars > 0.20:
         return True 
    else:
         return False


if __name__ == "__main__":
    with open("01.txt", "r", encoding="utf-8") as file:
        text = file.read()

    text = clean_text(text, alphabet)

    bigrams_in_encrypt = bigrams(text, alphabet, step=2)
    keys = generate_keys(frequent_bigrams, bigrams_in_encrypt, alphabet)

    print(keys)
    print(f"Кількість можливих ключів: {len(keys)}")

    best_texts = []
    for a, b in keys:
        decrypted = decrypt_affine(text, a, b, alphabet)
        if decrypted and is_valid_text(decrypted, impossible_bigrams):
            best_texts.append((a, b, decrypted))

    print(f"\nПідходящих текстів: {len(best_texts)}")

    for (a, b, text) in best_texts:
        print(f"\na = {a}, b = {b}")
        print(f"Текст: {text}")        