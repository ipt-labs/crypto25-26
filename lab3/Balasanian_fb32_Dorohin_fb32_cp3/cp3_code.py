import os
from collections import Counter
from itertools import permutations
from math import gcd
import glob

alphabet = "абвгдежзийклмнопрстуфхцчшщьыэюя"
alphabet_SET = set(alphabet)
alphabet_len = len(alphabet)
bigram_mod = alphabet_len * alphabet_len

char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
idx_to_char = {i: ch for i, ch in enumerate(alphabet)}


def egcd(a: int, b: int):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


def modular_inverse(a: int, m: int):
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m


def solve_congruence(a: int, b: int, m: int):
    g, x_coef, _ = egcd(a, m)
    if b % g != 0:
        return []
    x0 = (x_coef * (b // g)) % m
    step = m // g
    return [(x0 + k * step) % m for k in range(g)]


def bigram_to_number(bg: str) -> int:
    return char_to_idx[bg[0]] * alphabet_len + char_to_idx[bg[1]]


def number_to_bigram(num: int) -> str:
    return idx_to_char[num // alphabet_len] + idx_to_char[num % alphabet_len]


def try_read_with_encodings(path, encodings):
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, errors="ignore") as f:
                raw = f.read()
            return raw, enc
        except Exception:
            continue
    return None, None


def find_fallback_txt(preferred_names=None):
    if preferred_names is None:
        preferred_names = ["08.txt", "8.txt"]

    for name in preferred_names:
        if os.path.exists(name):
            return name

    list_txt = sorted(glob.glob("*.txt"))
    if list_txt:
        return list_txt[0]
    return None


def read_cipher_file(path: str = None, encoding="utf-8", strip_spaces=True):
    encodings_to_try = [encoding, "utf-8", "utf-8-sig", "cp1251", "cp866", "utf-16"]

    if path is None or not os.path.exists(path):
        fallback = find_fallback_txt(preferred_names=[path] if path else None)
        if fallback:
            print(f"Увага: файл '{path}' не знайдено. Використовую файл '{fallback}' як запасний варіант.")
            path = fallback
        else:
            print(f"Файл '{path}' не знайдено й не знайдено жодного .txt у поточній директорії.")
            return ""

    raw, used_enc = try_read_with_encodings(path, encodings_to_try)
    if raw is None:
        print(f"Не вдалося прочитати '{path}' з жодним із стандартних кодувань {encodings_to_try}.")
        return ""

    print(f"Файл '{path}' прочитано з кодуванням: {used_enc}")
    s = raw.lower().replace("ё", "е").replace("ъ", "ь")
    if strip_spaces:
        s = s.replace("\n", "").replace("\r", "").replace(" ", "")
        return s
    return "".join(ch for ch in s if ch in alphabet_SET)


def count_bigrams(text: str):
    n = len(text)
    overlap = Counter()
    non_overlap = Counter()
    for i in range(n - 1):
        overlap[text[i:i+2]] += 1
    for i in range(0, n - 1, 2):
        non_overlap[text[i:i+2]] += 1
    return overlap, non_overlap


def decrypt_affine_bigrams(cipher: str, a: int, b: int):
    a_inv = modular_inverse(a, bigram_mod)
    if a_inv is None:
        return None
    if len(cipher) % 2 != 0:
        cipher = cipher[:-1]
    parts = []
    for i in range(0, len(cipher), 2):
        bg = cipher[i:i+2]
        if len(bg) != 2 or (bg[0] not in char_to_idx) or (bg[1] not in char_to_idx):
            return None
        Y = bigram_to_number(bg)
        X = (a_inv * (Y - b)) % bigram_mod
        parts.append(number_to_bigram(X))
    return "".join(parts)


def looks_like_russian(text: str) -> bool:
    if not text:
        return False
    total = len(text)
    common = 'оеаинтсрвлкмдпуя'
    rare = 'фщъэ'
    freq_common = sum(text.count(ch) for ch in common) / total
    freq_rare = sum(text.count(ch) for ch in rare) / total
    if total < 200:
        return freq_common > 0.48 and freq_rare < 0.06
    return freq_common > 0.50 and freq_rare < 0.03


def make_key_candidates(lang_pair, cipher_pair):
    X1 = bigram_to_number(lang_pair[0])
    X2 = bigram_to_number(lang_pair[1])
    Y1 = bigram_to_number(cipher_pair[0])
    Y2 = bigram_to_number(cipher_pair[1])

    deltaX = (X1 - X2) % bigram_mod
    deltaY = (Y1 - Y2) % bigram_mod

    if deltaX % bigram_mod == 0:
        return []

    a_candidates = solve_congruence(deltaX, deltaY, bigram_mod)
    results = []
    for a in a_candidates:
        if gcd(a, bigram_mod) != 1:
            continue
        b = (Y1 - a * X1) % bigram_mod
        results.append((a, b))
    return results


def attack_affine_bigrams(file_path="08.txt", encoding="utf-8",
                          language_bigrams=None,
                          output_file="cp3_original.txt",
                          assume_clean=True):
    if language_bigrams is None:
        language_bigrams = ['ст', 'но', 'то', 'на', 'ен']

    text = read_cipher_file(file_path, encoding=encoding, strip_spaces=assume_clean)
    if len(text) < 2:
        print("Файл містить замало символів.")
        return None, None

    overlap, non_overlap = count_bigrams(text)
    source = non_overlap if sum(non_overlap.values()) > 0 else overlap
    top5 = [bg for bg, _ in source.most_common(5)]
    print("5 найчастіших біграм шифртексту:", top5)

    if len(top5) < 2:
        print("Замало біграм для перебору.")
        return None, None

    lang_pairs = list(permutations(language_bigrams, 2))
    cipher_pairs = list(permutations(top5, 2))
    total_checks = len(lang_pairs) * len(cipher_pairs)
    print(f"\nПочинаємо перебір {total_checks} співставлень пар...")

    tried = 0
    seen_keys = set()

    for lp in lang_pairs:
        for cp in cipher_pairs:
            candidates = make_key_candidates(lp, cp)
            if candidates:
                print(f"Співставлення {lp} -> {cp}: знайдено кандидатів {len(candidates)}")
            for a, b in candidates:
                if (a, b) in seen_keys:
                    continue
                seen_keys.add((a, b))
                tried += 1

                plaintext = decrypt_affine_bigrams(text, a, b)
                if plaintext is None:
                    continue

                if looks_like_russian(plaintext):
                    print("\nЗнайдено осмислений текст")
                    print(f"Ключ (a, b) = ({a}, {b})")
                    print(f"Знайдено після {tried} унікальних перевірок.")
                    print("Початок дешифрування:", plaintext[:50])
                    try:
                        with open(output_file, "w", encoding="utf-8") as out:
                            out.write(plaintext)
                        print(f"Дешифровка збережена у {output_file}")
                    except Exception as e:
                        print("Помилка збереження:", e)
                    return (a, b), plaintext

    print(f"\nПеревірено {tried} унікальних кандидатів. Результат: нічого не знайдено.")
    return None, None


def demo_point1():
    print("Пункт 1: обернений елемент і розв'язки лінійних порівнянь\n")
    examples = [(3, 26), (7, 26), (4, 12)]
    for a, m in examples:
        inv = modular_inverse(a, m)
        if inv is None:
            print(f"Оберненого елемента для a={a} (mod {m}) НЕ ІСНУЄ (gcd != 1).")
        else:
            print(f"a={a} (mod {m}) -> a^(-1) = {inv}, перевірка: (a*inv) % m = {(a*inv) % m}")

    print("\nПриклади розв'язування a*x ≡ b (mod m):")
    tests = [(4, 8, 12), (6, 10, 14), (5, 3, 26), (6, 7, 14)]
    for a, b, m in tests:
        sols = solve_congruence(a, b, m)
        if not sols:
            print(f"  {a}*x ≡ {b} (mod {m}) — рішень нема.")
        else:
            print(f"  {a}*x ≡ {b} (mod {m}) — знайдено {len(sols)} рішень: {sorted(sols)}")
    print("\nКінець демонстрації пункту 1 \n")


if __name__ == "__main__":
    demo_point1()
    attack_affine_bigrams(file_path="08.txt", encoding="utf-8", assume_clean=True)