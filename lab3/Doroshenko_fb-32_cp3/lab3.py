'''
Завдання 1: Математичні примітиви
'''

# Розширений алгоритм Евкліда.
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = extended_gcd(b % a, a)
        return g, x - (b // a) * y, y

# Знаходження оберненого елемента a^(-1) за модулем m.
def mod_inverse(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        return None
    else:
        return x % m

# Розв'язання лінійного порівняння: ax ≡ b (mod n).
def solve_linear_congruence(a, b, n):
    g, x, y = extended_gcd(a, n)

    if b % g != 0:
        return []

    # a/g * x ≡ b/g (mod n/g)
    x0 = (x * (b // g)) % n

    solutions = []
    step = n // g
    for k in range(g):
        solutions.append((x0 + k * step) % n)

    return solutions

# Перевірка роботи 1 завдання
print("\n--- Перевірка 1 завдання ---")
try:
    # Тест 1: Обернений елемент
    a = 3
    m = 11
    inv = mod_inverse(a, m)

    print(f"Обернений елемент до {a} по модулю {m} = {inv}")

    # Тест 2: Лінійне порівняння з декількома розв'язками
    a, b, n = 2, 4, 6
    sols = solve_linear_congruence(a, b, n)

    print(f"Розв'язки порівняння {a}x ≡ {b} (mod {n}): {sols}")

except Exception as e:
    print(f"ПОМИЛКА Завдання 1: {e}")


'''
Завдання 2: Обробка текстового документа
'''

import collections


ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
M = len(ALPHABET)
CHAR_TO_INDEX = {char: idx for idx, char in enumerate(ALPHABET)}

# Зчитування файлу, очистка тексту, розбиття на біграми та знаходження найчастіших.
def get_bigram_indices(filename):
    content = ""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Файл не знайдено: {filename}")
        return []

    clean_text = "".join([c for c in content.lower() if c in ALPHABET])

    if len(clean_text) % 2 != 0:
        clean_text += "а"

    # Формування списку індексів
    indices = []
    for i in range(0, len(clean_text), 2):
        x1 = CHAR_TO_INDEX[clean_text[i]]
        x2 = CHAR_TO_INDEX[clean_text[i+1]]
        indices.append(x1 * M + x2)

    return indices

# Перевірка роботи 2 завдання
try:
    print("\n--- Перевірка 2 завдання ---")

    target_file = "tasks/cp3/variants.utf8/06.txt"

    print(f"Аналіз файлу: {target_file}")

    cipher_indices = get_bigram_indices(target_file)

    if cipher_indices:
        print(f"Всього біграм: {len(cipher_indices)}")

        ctr = collections.Counter(cipher_indices)
        top_5_tuples = ctr.most_common(5)

        top_5_indices = [item[0] for item in top_5_tuples]

        print(f"Топ-5 найчастіших біграм (числа): {top_5_indices}")

        print("Розшифровка:")
        for idx in top_5_indices:
            c1 = ALPHABET[idx // M]
            c2 = ALPHABET[idx % M]
            print(f"    {idx} -> '{c1}{c2}'")

except Exception as e:
    print(f"ПОМИЛКА Завдання 2: {e}")

'''
Завдання 3: Пошук кандидатів на ключ
'''

M2 = M * M

# Генерує список кандидатів (a, b)
def generate_keys_from_top5(top_5_indices):
    # Найчастіші біграми мови
    top_lang_str = ["ст", "но", "то", "на", "ен"]

    # Переводимо їх у числа X
    top_lang_indices = []
    for s in top_lang_str:
        idx = CHAR_TO_INDEX[s[0]] * M + CHAR_TO_INDEX[s[1]]
        top_lang_indices.append(idx)

    print(f"Топ-5 біграм мови (X): {top_lang_indices}")
    print(f"Топ-5 біграм шифртексту (Y): {top_5_indices}")

    found_keys = set()

    # Перебір пар біграм мови (X1, X2)
    for i in range(len(top_lang_indices)):
        for j in range(len(top_lang_indices)):
            if i == j: continue

            X1 = top_lang_indices[i]
            X2 = top_lang_indices[j]

            # Перебір пар біграм шифртексту (Y1, Y2)
            for k in range(len(top_5_indices)):
                for l in range(len(top_5_indices)):
                    if k == l: continue

                    Y1 = top_5_indices[k]
                    Y2 = top_5_indices[l]

                    # Розв'язання рівняння: a * (X1 - X2) = (Y1 - Y2) mod m^2
                    diff_X = (X1 - X2) % M2
                    diff_Y = (Y1 - Y2) % M2

                    candidates_a = solve_linear_congruence(diff_X, diff_Y, M2)

                    for a in candidates_a:
                        if extended_gcd(a, M)[0] != 1:
                            continue

                        # Знаходження b: b = Y1 - a*X1 mod m^2
                        b = (Y1 - a * X1) % M2
                        found_keys.add((a, b))

    return list(found_keys)

# Перевірка роботи 3 завдання
if __name__ == "__main__":
    print("\n--- Перевірка 3 завдання ---")

    print("Починаємо перебір варіантів...")
    candidates = generate_keys_from_top5(top_5_indices)

    print(f"\nЗгенеровано унікальних ключів: {len(candidates)}")
    print("    Кандидати на ключ (a, b):")
    for k in candidates:
        print(f"    {k}")
