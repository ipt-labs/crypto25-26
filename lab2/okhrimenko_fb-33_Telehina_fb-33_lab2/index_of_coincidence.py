import os
import math

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

# індекс відповідності


def calculate_ioc(text: str) -> float:
    n = len(text)
    if n < 2:
        return 0.0

    # Підрахунок частот N_t(Y)
    freq = {}
    for char in ALPHABET:
        freq[char] = 0

    for char in text:
        if char in freq:
            freq[char] += 1

    # N_t(Y) * (N_t(Y) - 1)
    sum_nt_product = 0
    for count in freq.values():
        sum_nt_product += count * (count - 1)

    # I(Y)
    ioc = sum_nt_product / (n * (n - 1))

    return ioc

# IoC для ВТ та всіх ШТ


def compare_iocs():
    files_to_analyze = {
        "Plaintext (PT)": "cleaned_text.txt",
        "Ciphertext (r=2)": "ciphertext_r=2.txt",
        "Ciphertext (r=3)": "ciphertext_r=3.txt",
        "Ciphertext (r=4)": "ciphertext_r=4.txt",
        "Ciphertext (r=5)": "ciphertext_r=5.txt",
        "Ciphertext (r=16)": "ciphertext_r=16.txt"
    }

    # Теоретичні значення для порівняння I_0 = 1/m = 1/32
    I_RANDOM = 1 / M
    I_EXPECTED = 0.055

    print("--- Index of Coincidence (IoC) Calculation Results ---")
    print(
        f"Theoretical IoC for a random alphabet (I_0 = 1/32): {I_RANDOM:.5f}")
    print(
        f"Expected IoC for Russian language (I_X ≈ MI): {I_EXPECTED:.5f} (For comparison)")
    print("-" * 50)

    results = {}

    for label, filename in files_to_analyze.items():
        if not os.path.exists(filename):
            print(f"File {filename} not found... Skipping")
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read().strip()

        ioc_value = calculate_ioc(text)
        results[label] = ioc_value

    print(f"{'Text Type':<25} | {'IoC (I(Y))':<15} | {'Comparison'}")
    print("-" * 50)
    for label, ioc_value in results.items():
        comparison = ""
        if "Plaintext" in label:
            comparison = f"≈ MI(language)"
        else:
            comparison = f"≈ I_0 (1/32)"

        print(f"{label:<25} | {ioc_value:<15.5f} | {comparison}")

    print(
        f"1. The IoC of the plaintext should be close to I_EXPECTED ({I_EXPECTED:.5f}) (high)")
    print(
        f"2. The IoC of all ciphertexts (r≥2) should be close to I_RANDOM ({I_RANDOM:.5f}) (low)")


if __name__ == '__main__':
    compare_iocs()
