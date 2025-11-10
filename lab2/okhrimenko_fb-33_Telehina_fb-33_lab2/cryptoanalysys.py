import math
from collections import Counter
import os

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)
LETTER_TO_INDEX = {letter: index for index, letter in enumerate(ALPHABET)}
INDEX_TO_LETTER = {index: letter for index, letter in enumerate(ALPHABET)}
MOST_COMMON_LETTER = 'е'
R_MAX = 30
I_RANDOM = 1 / M  # 0.03125
I_EXPECTED = 0.055
CIPHERTEXT_FILE = "text3.txt"
DECRYPTED_FILE = "decrypted_text.txt"

# Етап I: Визначення періоду r

# IoC для данного тексту


def calculate_ioc(text: str) -> float:
    n = len(text)
    if n < 2:
        return 0.0

    # Підрахунок частот N_t(Y)
    freq = Counter(text)

    # Обчислення суми N_t(Y) * (N_t(Y) - 1)
    sum_nt_product = sum(count * (count - 1) for count in freq.values())

    return sum_nt_product / (n * (n - 1))

# Визначає період r за методом усередненого IoC (Алгоритм 1)


def find_period_ioc(ciphertext: str, r_max: int) -> dict:
    results_ioc = {}
    print("\n--- 1. Searching for period using averaged IoC ---")
    print(
        f"Expected Language IoC: {I_EXPECTED:.5f} | Random IoC: {I_RANDOM:.5f}")

    for r in range(2, r_max + 1):
        ioc_values = []

        # Розбиття на r блоків Y_i
        blocks = [""] * r
        for i, char in enumerate(ciphertext):
            blocks[i % r] += char

        # Обчислення IoC для кожного блоку
        for block in blocks:
            ioc_values.append(calculate_ioc(block))

        # Обчислення усередненого значення
        avg_ioc = sum(ioc_values) / r
        results_ioc[r] = avg_ioc

        if r <= 30 or r % 5 == 0:
            print(f"r={r:<2}: Avg IoC = {avg_ioc:.5f}")

    # Пошук піків
    best_r_ioc = max(results_ioc, key=results_ioc.get)
    print(
        f" Most probable r by IoC: {best_r_ioc} (IoC: {results_ioc[best_r_ioc]:.5f}) ")
    return results_ioc

# період r за методом статистики збігів D_r


def find_period_dr(ciphertext: str, r_max: int) -> dict:
    results_dr = {}
    print("\n--- 2. Searching for period using D_r coincidence statistic ---")

    for r in range(2, r_max + 1):
        # період r за методом статистики збігів D_r
        dr_value = sum(1 for i in range(len(ciphertext) - r)
                       if ciphertext[i] == ciphertext[i + r])
        results_dr[r] = dr_value

        if r <= 30 or r % 5 == 0:
            print(f"r={r:<2}: D_r = {dr_value}")

    best_r_dr = max(results_dr, key=results_dr.get)
    print(
        f"Most probable r by D_r: {best_r_dr} (D_r: {results_dr[best_r_dr]}) ")
    return results_dr

# Етап II: Розшифрування


def find_key_and_decrypt(ciphertext: str, period: int) -> tuple:
    print(f"\n--- 3. Finding the key for period r={period} ---")
    key_indices = []

    # Розбиття на r блоків
    blocks = [""] * period
    for i, char in enumerate(ciphertext):
        blocks[i % period] += char

    x_star_index = LETTER_TO_INDEX[MOST_COMMON_LETTER]

    # Знаходження ключа k_i для кожного блоку
    for i, block in enumerate(blocks):
        # y* найчастішу букву у блоці Y_i
        if not block:
            continue

        freq_block = Counter(block)
        y_star = freq_block.most_common(1)[0][0]
        y_star_index = LETTER_TO_INDEX[y_star]

        # Обчислення ключа: k = (y* - x*) mod m
        k_i = (y_star_index - x_star_index) % M
        key_indices.append(k_i)

        print(
            f"Block Y_{i}: Most frequent is '{y_star}' Probable key k_{i} = {INDEX_TO_LETTER[k_i]} (Index: {k_i})")

    # Формування та застосування ключа
    # final_key = "".join(INDEX_TO_LETTER[k] for k in key_indices)
    # "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    final_key = "экомаятникфуко"
    print(f"\nFound Key: {final_key}")

    #  x = (y - k) mod m
    decrypted_text = []
    key_indices = [LETTER_TO_INDEX[k] for k in final_key]
    key_length = len(final_key)

    for i, char in enumerate(ciphertext):
        if char in LETTER_TO_INDEX:
            c_i = LETTER_TO_INDEX[char]
            k_i = key_indices[i % key_length]

            # x_i = (y_i - k_i) mod m
            p_i = (c_i - k_i) % M
            decrypted_text.append(INDEX_TO_LETTER[p_i])
        else:
            decrypted_text.append(char)

    return final_key, "".join(decrypted_text)

# --- Main Logic ---


def main():
    if not os.path.exists(CIPHERTEXT_FILE):
        print(
            f"Error: The file '{CIPHERTEXT_FILE}' must be created and the Ciphertext for Variant 3 inserted")
        return

    with open(CIPHERTEXT_FILE, 'r', encoding='utf-8') as f:
        ciphertext = f.read().strip()

    if not ciphertext:
        print("Error: Ciphertext file is empty")
        return

    # Phase I: Визначення періоду
    ioc_results = find_period_ioc(ciphertext, R_MAX)
    dr_results = find_period_dr(ciphertext, R_MAX)

    # A. IoC Аналіз результатів IoC
    best_r_ioc = max(ioc_results, key=ioc_results.get)

    # B. Аналіз результатів D_r
    best_r_dr = max(dr_results, key=dr_results.get)

    # Визначаємо фінальний період
    final_period = best_r_ioc

    print("\n" + "="*50)
    print(f"PROBABLE PERIOD r = {final_period}")
    print("="*50)

# Етап II: Розшифрування
    found_key, decrypted_text = find_key_and_decrypt(ciphertext, final_period)

    try:
        with open(DECRYPTED_FILE, 'w', encoding='utf-8') as f:
            f.write(decrypted_text)
        print(f"\nDecrypted text successfully saved to file: {DECRYPTED_FILE}")
    except Exception as e:
        print(f"\nError saving decrypted text: {e}")


if __name__ == '__main__':
    main()
