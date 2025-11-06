import math
from typing import List, Tuple, Set

ALPHABET_STR = "абвгдежзийклмнопрстуфхцчшщьыэюя"
M = len(ALPHABET_STR)
M_SQUARED = M * M

CHAR_TO_INT = {char: i for i, char in enumerate(ALPHABET_STR)}


def egcd(a: int, n: int) -> Tuple[int, int]:
    r_prev, r_curr = a, n
    u_prev, u_curr = 1, 0

    while r_curr != 0:
        q = r_prev // r_curr
        r_prev, r_curr = r_curr, r_prev - q * r_curr
        u_prev, u_curr = u_curr, u_prev - q * u_curr

    return r_prev, u_prev

def mod_inverse(a: int, n: int) -> int | None:
    gcd, u = egcd(a, n)
    if gcd != 1:
        return None
    else:
        return u % n

def solve_linear_congruence(a: int, b: int, n: int) -> List[int]:
    a = a % n
    b = b % n

    d, _ = egcd(a, n)

    if d == 1:
        a_inv = mod_inverse(a, n)
        return [(a_inv * b) % n]
    else:
        if b % d != 0:
            return []
        else:
            a1 = a // d
            b1 = b // d
            n1 = n // d

            a1_inv = mod_inverse(a1, n1)
            x0 = (a1_inv * b1) % n1

            return [x0 + k * n1 for k in range(d)]

def bigram_to_int(bigram: str) -> int:
    try:
        x1 = CHAR_TO_INT[bigram[0]]
        x2 = CHAR_TO_INT[bigram[1]]
        return x1 * M + x2
    except KeyError as e:
        print(f"Помилка: символ '{e.args[0]}' відсутній в алфавіті")
        return -1

def find_key_candidates(top_plain_bgs: List[str], top_cipher_bgs: List[str]) -> Set[Tuple[int, int]]:
    candidates = set()

    for i in range(len(top_plain_bgs)):
        for j in range(len(top_plain_bgs)):
            if i == j: continue

            X_star = bigram_to_int(top_plain_bgs[i])
            X_star_star = bigram_to_int(top_plain_bgs[j])

            A = (X_star - X_star_star) % M_SQUARED

            for k in range(len(top_cipher_bgs)):
                for l in range(len(top_cipher_bgs)):
                    if k == l: continue

                    Y_star = bigram_to_int(top_cipher_bgs[k])
                    Y_star_star = bigram_to_int(top_cipher_bgs[l])

                    B = (Y_star - Y_star_star) % M_SQUARED

                    possible_as = solve_linear_congruence(A, B, M_SQUARED)

                    for a in possible_as:
                        if math.gcd(a, M) != 1:
                            continue

                        b = (Y_star - a * X_star) % M_SQUARED

                        candidates.add((a, b))


    return candidates

def main():
    top_plain_bgs = ["ст", "но", "то", "на", "ен"]
    top_cipher_bgs = ["аф", "яф", "дю", "ап", "нф"]
    output_filename = "key_candidates.txt"

    print(f"Модуль: m^2 = {M_SQUARED}\n")
    print(f"Найчастіші біграми мови: {top_plain_bgs}")
    print(f"Найчастіші біграми шифртексту: {top_cipher_bgs}\n")

    candidates = find_key_candidates(top_plain_bgs, top_cipher_bgs)

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            for a, b in candidates:
                f.write(f"{a},{b}\n")

        print(f"Знайдено {len(candidates)} унікальних кандидатів")
        print(f"Кандидати успішно збережено у файл '{output_filename}'")

    except IOError as e:
        print(f"Помилка запису у файл '{output_filename}': {e}")

    if not candidates:
        print("Кандидатів не знайдено (можливо, неправильні біграми шифртексту?)")


if __name__ == "__main__":
    main()