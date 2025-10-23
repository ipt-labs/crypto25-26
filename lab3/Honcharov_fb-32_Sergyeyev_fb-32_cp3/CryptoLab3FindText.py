import re
from collections import defaultdict
import math
import sys

ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"

STANDARD_RUSSIAN_FREQUENCIES = {
    'о': 0.1098, 'е': 0.0848, 'а': 0.0800, 'и': 0.0734,
    'н': 0.0670, 'т': 0.0620, 'с': 0.0540, 'р': 0.0470,
    'в': 0.0450, 'л': 0.0440, 'к': 0.0350, 'м': 0.0320,
    'д': 0.0300, 'п': 0.0280, 'у': 0.0260, 'я': 0.0200,
    'ы': 0.0190, 'ь': 0.0174, 'г': 0.0170, 'з': 0.0160,
    'б': 0.0160, 'ч': 0.0140, 'й': 0.0120, 'х': 0.0100,
    'ж': 0.0090, 'ш': 0.0070, 'ю': 0.0060, 'ц': 0.0050,
    'щ': 0.0040, 'э': 0.0030, 'ф': 0.0020
}



def get_relative_frequencies(text):
    text = text.lower()
    text = text.replace('ё', 'е').replace('ъ', 'ь')
    frequencies = defaultdict(int)
    total_symbols = 0
    for char in text:
        if char in ALPHABET:
            frequencies[char] += 1
            total_symbols += 1 
    if total_symbols == 0:
        return {}
    relative_frequencies = {}
    for char, count in frequencies.items():
        relative_frequencies[char] = count / total_symbols
        
    return relative_frequencies


def compare_distributions(cipher_freq, reference_freq):
    score = 0
    for char in ALPHABET:
        cipher_p = cipher_freq.get(char, 0)
        ref_p = reference_freq.get(char, 0)
        score += (cipher_p - ref_p) ** 2  
    return score



def main():
    INPUT_FILE = "all_decryptions.txt"
    best_match_text = None
    best_match_line_number = -1
    lowest_score = float('inf')

    print(f"Читання файла '{INPUT_FILE}'...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            all_ciphertexts = f.read().splitlines()
    except FileNotFoundError:
        print(f"Помилка: файл '{INPUT_FILE}' не знайдений.")
        sys.exit(1)
    except Exception as e:
        print(f"Помилка при читанні файла: {e}.")
        sys.exit(1)

    print(f"Знайдено {len(all_ciphertexts)} строк. Починаємо аналіз...")
    print("-" * 30)

    for line_number, raw_text in enumerate(all_ciphertexts, 1):
        if not raw_text.strip():
            continue
        cipher_frequencies = get_relative_frequencies(raw_text)
        if not cipher_frequencies:
            continue  
        score = compare_distributions(cipher_frequencies, STANDARD_RUSSIAN_FREQUENCIES)
        print(f"Строка: {line_number:03d} | Оцінка: {score:.8f}")
        if score < lowest_score:
            lowest_score = score
            best_match_text = raw_text
            best_match_line_number = line_number

    print("-" * 30)
    if best_match_text:
        print(f"Аналіз завершений.")
        print(f"Найбільше співпадіннь частот у строці: {best_match_line_number}")
        print(f"Оцінка(нижче - краще): {lowest_score:.8f}")
        print("\nПочаток текста:")
        print(best_match_text[:100] + ("..." if len(best_match_text) > 100 else ""))
    else:
        print("Аналіз завершений. Текст не знайдений.")

if __name__ == "__main__":
    main()