import os
from collections import Counter
from itertools import permutations
from math import gcd

ALPHABET = "абвгдежзийклмнопрстуфхцчшщьыэюя"
ALPHABET_SET = set(ALPHABET)
ALPHABET_SIZE = len(ALPHABET)
BIGRAM_MOD = ALPHABET_SIZE ** 2

letter_to_num = {ch: i for i, ch in enumerate(ALPHABET)}
num_to_letter = {i: ch for i, ch in enumerate(ALPHABET)}


def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


def mod_inverse(a, m):
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m


def solve_linear_congruence(a, b, m):
    g, x, _ = extended_gcd(a, m)
    if b % g != 0:
        return []

    x0 = (x * (b // g)) % m
    step = m // g

    return [(x0 + i * step) % m for i in range(g)]


def read_ciphertext(path, encoding="utf8", assume_clean=True):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл {path} не знайдено")

    try:
        with open(path, "r", encoding=encoding, errors="ignore") as f:
            raw = f.read()
    except Exception as e:
        print(f"Error reading file {path} with encoding {encoding}: {e}")
        return ""

    s = raw.lower()
    s = s.replace("ё", "е").replace("ъ", "ь")

    if assume_clean:
        s = s.replace("\n", "").replace("\r", "").replace(" ", "")
        return s

    return "".join(ch for ch in s if ch in ALPHABET_SET)


def count_bigrams_from_text(text):
    n = len(text)
    overlap = Counter()
    non_overlap = Counter()

    for i in range(0, n - 1):
        overlap[text[i:i + 2]] += 1

    for i in range(0, n - 1, 2):
        non_overlap[text[i:i + 2]] += 1

    return overlap, non_overlap


def bigram_to_num(bigram):
    return letter_to_num[bigram[0]] * ALPHABET_SIZE + letter_to_num[bigram[1]]


def num_to_bigram(num):
    return num_to_letter[num // ALPHABET_SIZE] + num_to_letter[num % ALPHABET_SIZE]


def decrypt_affine_bigram(ciphertext, a, b):
    a_inv = mod_inverse(a, BIGRAM_MOD)
    if a_inv is None:
        return None

    res = []

    if len(ciphertext) % 2 != 0:
        ciphertext = ciphertext[:-1]

    for i in range(0, len(ciphertext), 2):
        bg = ciphertext[i:i + 2]

        if len(bg) != 2 or bg[0] not in letter_to_num or bg[1] not in letter_to_num:
            return None

        Y = bigram_to_num(bg)
        X = (a_inv * (Y - b)) % BIGRAM_MOD
        res.append(num_to_bigram(X))

    return "".join(res)


def is_meaningful(text):
    if not text:
        return False

    total = len(text)
    common_letters = 'оеаинтсрвлкмдпуя'
    rare_letters = 'фщъэ'

    freq_common = sum(text.count(ch) for ch in common_letters) / total
    freq_rare = sum(text.count(ch) for ch in rare_letters) / total

    if total < 200:
        return freq_common > 0.48 and freq_rare < 0.06
    return freq_common > 0.50 and freq_rare < 0.03


def generate_key_candidates_from_pair_pairs(lang_pair, cipher_pair):
    X1 = bigram_to_num(lang_pair[0])
    X2 = bigram_to_num(lang_pair[1])
    Y1 = bigram_to_num(cipher_pair[0])
    Y2 = bigram_to_num(cipher_pair[1])

    delta_X = (X1 - X2) % BIGRAM_MOD
    delta_Y = (Y1 - Y2) % BIGRAM_MOD

    candidates = []

    if delta_X % BIGRAM_MOD == 0:
        if delta_Y % BIGRAM_MOD != 0:
            return []

        return []

    a_solutions = solve_linear_congruence(delta_X, delta_Y, BIGRAM_MOD)

    for a in a_solutions:
        if gcd(a, BIGRAM_MOD) != 1:
            continue

        b = (Y1 - a * X1) % BIGRAM_MOD
        candidates.append((a, b))

    return candidates


def attack_affine_bigrams(file_path="02.txt", encoding="unf8",
                          language_bigrams=None,
                          output_file="decrypted.txt",
                          assume_clean=True):
    if language_bigrams is None:
        language_bigrams = ['ст', 'но', 'то', 'на', 'ен']

    text = read_ciphertext(file_path, encoding=encoding, assume_clean=assume_clean)
    if len(text) < 2:
        print("Файл містить замало символів після зчитування.")
        return None, None

    overlap, non_overlap = count_bigrams_from_text(text)
    source = non_overlap if sum(non_overlap.values()) > 0 else overlap
    top5 = [bg for bg, _ in source.most_common(5)]
    print("5 найчастіших біграм шифртексту :", top5)

    if len(top5) < 2:
        print("Надто мало біграм для атаки.")
        return None, None

    lang_pairs = list(permutations(language_bigrams, 2))
    cipher_pairs = list(permutations(top5, 2))

    print(f"\nПочинаємо перебір {len(lang_pairs) * len(cipher_pairs)} можливих співставлень пар...")

    tested = 0
    checked_keys = set()

    for lp in lang_pairs:
        for cp in cipher_pairs:
            cand = generate_key_candidates_from_pair_pairs(lp, cp)

            if cand:
                print(f"-> Співставлення: {lp} -> {cp}. Знайдено кандидати на ключ (a, b): {cand}")

            for a, b in cand:
                if (a, b) in checked_keys:
                    continue
                checked_keys.add((a, b))
                tested += 1

                dec = decrypt_affine_bigram(text, a, b)

                if dec is None:
                    continue

                if is_meaningful(dec):
                    print("\nЗНАЙДЕНО ЗМІСТОВНИЙ ТЕКСТ")
                    print(f"Ключ (a, b) = ({a}, {b})")
                    print(f"Знайдено після {tested} унікальних перевірок.")
                    print("\nПочаток дешифрованого тексту:", dec[:20])

                    try:
                        with open(output_file, "w", encoding="utf-8") as out:
                            out.write(dec)
                        print(f"\nДешифрований текст збережено у '{output_file}'")
                    except Exception as e:
                        print(f"Не вдалося зберегти файл: {e}")

                    return (a, b), dec

    print(f"\nПеревірено {tested} унікальних кандидатів.")
    print("Не знайдено змістовного тексту автоматично.")
    return None, None


if __name__ == "__main__":
    attack_affine_bigrams(file_path="02.txt", encoding="utf8", assume_clean=True)
