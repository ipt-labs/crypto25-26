import re
from collections import Counter
from math import gcd

def clean_text(text: str) -> str:
    text = text.lower().replace("ё", "е").replace("ъ", "ь")
    text = re.sub(r'[^а-я]', '', text)
    return text


# частоти біграм
def bigram_freq(text: str, step=2, top_n=5):
    bigrams = [text[i:i+2] for i in range(0, len(text)-1, step)]
    freq = Counter(bigrams)
    total = sum(freq.values())
    print("\n- РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ ЧАСТОТ БІГРАМ -\n")
    print("-" * 45)
    print(f"{'№':<3} | {'Біграма':<8} | {'Кількість':<10} | {'Частота':<10}")
    print("-" * 45)
    for i, (bg, count) in enumerate(freq.most_common(top_n), 1):
        freq_rel = count / total
        print(f"{i:<3} | {bg:<8} | {count:<10} | {freq_rel:.7f}")
    print("-" * 45)
    return [bg for bg, _ in freq.most_common(top_n)]


# математичні підпрограми
def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a, mod):
    g, x, _ = egcd(a, mod)
    if g != 1:
        return None
    return x % mod

def solve_linear_congruence(a, b, mod):
    d = gcd(a, mod)
    if b % d != 0:
        return []
    a1, b1, mod1 = a // d, b // d, mod // d
    inv = mod_inverse(a1, mod1)
    if inv is None:
        return []
    x0 = (inv * b1) % mod1
    return [(x0 + k * mod1) % mod for k in range(d)]


# операції з біграмами 
ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
m = len(ALPHABET)
MOD = m * m  # 31^2 = 961

def bigram_to_num(bi: str) -> int:
    return ALPHABET.index(bi[0]) * m + ALPHABET.index(bi[1])

def num_to_bigram(num: int) -> str:
    return ALPHABET[num // m] + ALPHABET[num % m]

def decrypt_bigram(Y: int, a: int, b: int):
    a_inv = mod_inverse(a, MOD)
    if a_inv is None:
        return None
    return (a_inv * ((Y - b) % MOD)) % MOD

def decrypt_text(cipher: str, a: int, b: int):
    if len(cipher) % 2 != 0:
        cipher = cipher[:-1]
    res = []
    for i in range(0, len(cipher), 2):
        Y = bigram_to_num(cipher[i:i+2])
        X = decrypt_bigram(Y, a, b)
        if X is None:
            return None
        res.append(num_to_bigram(X))
    return ''.join(res)


# перевірка осмисленості
def is_meaningful(text: str):
    cnt = Counter(text)
    total = sum(cnt.values())
    if total == 0:
        return False
    common = sum(cnt.get(ch, 0) for ch in "оеа") / total
    rare = sum(cnt.get(ch, 0) for ch in "фщ") / total
    return common > 0.2 and rare < 0.02 and any(w in text for w in ["на", "не", "то", "он", "она"])


# пошук ключів
def find_keys(X1, X2, Y1, Y2):
    dX = (X1 - X2) % MOD
    dY = (Y1 - Y2) % MOD
    g = gcd(dX, MOD)
    a_list = solve_linear_congruence(dX, dY, MOD)
    keys = []
    for a in a_list:
        b = (Y1 - a * X1) % MOD
        keys.append((dX, dY, g, a, b))
    return keys


# main
def main():
    print("Лабораторна робота №3: Криптоаналіз афінної підстановки біграм")

    with open("V12.txt", "r", encoding="utf-8") as f:
        raw = f.read()
    cipher = clean_text(raw)
    print(f"\nДовжина шифртексту після очищення: {len(cipher)} символів")

    top_cipher = bigram_freq(cipher, step=2, top_n=5)
    lang_top = ['ст', 'но', 'то', 'на', 'ен']

    print("\n- ТАБЛИЦЯ ОБЧИСЛЕНЬ ДЛЯ СИСТЕМИ (1): Пошук ключів (a, b) -\n")
    header = f"{'№':<3} | {'X1(біг)':<9} | {'X2(біг)':<9} | {'Y1(біг)':<9} | {'Y2(біг)':<9} | {'dX':<5} | {'dY':<5} | {'gcd':<5} | {'a':<6} | {'b':<6}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))


    all_pairs = []
    checked = set()
    num = 0

    for X1 in lang_top:
        for X2 in lang_top:
            if X1 == X2:
                continue
            X1n, X2n = bigram_to_num(X1), bigram_to_num(X2)
            for Y1 in top_cipher:
                for Y2 in top_cipher:
                    if Y1 == Y2:
                        continue
                    Y1n, Y2n = bigram_to_num(Y1), bigram_to_num(Y2)
                    for dX, dY, g, a, b in find_keys(X1n, X2n, Y1n, Y2n):
                        if (a, b) not in checked:
                            checked.add((a, b))
                            all_pairs.append((a, b))
                            num += 1
                            print(f"{num:<3} | {X1+'('+str(X1n)+')':<9} | {X2+'('+str(X2n)+')':<9} | "
                                  f"{Y1+'('+str(Y1n)+')':<9} | {Y2+'('+str(Y2n)+')':<9} | "
                                  f"{dX:<5} | {dY:<5} | {g:<5} | {a:<6} | {b:<6}")
    print("-" * len(header))
    print(f"Усього знайдено {len(all_pairs)} унікальних пар (a, b).")

    found = []
    for a, b in all_pairs:
        plain = decrypt_text(cipher, a, b)
        if plain and is_meaningful(plain):
            found.append((a, b, plain))

    print("\n- ПЕРЕВІРКА ПРАВИЛЬНОГО КЛЮЧА -")
    if found:
        for i, (a, b, text) in enumerate(found, 1):
            print(f"\nВаріант {i}:  a = {a},  b = {b}")

            print("\nДешифрований текст:\n")
            print(text)
            print("-" * 80)

        filename = f"decrypted_a{a}_b{b}.txt"
        with open(filename, "w", encoding="utf-8") as f_out:
            f_out.write(text)
        print(f"(Текст збережено у файл: {filename})")

        print(f"\nЗагальна кількість осмислених варіантів: {len(found)}")
    else:
        print("\nОсмислений текст не знайдено.")


if __name__ == "__main__":
    main()

