from collections import Counter
import re
import os
from pathlib import Path

def get_non_overlapping_bigram_counts(text: str) -> Counter:
    bigrams = [text[i:i+2] for i in range(0, len(text) - 1, 2)]
    counts = Counter(bigrams)
    return counts

def main():
    filename_to_find = "05 (1).txt"
    script_dir = Path(__file__).parent
    filepath = script_dir / filename_to_find
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            ciphertext = file.read()
        cleaned_text = re.sub(r'\s+', '', ciphertext)
        bigram_counts = get_non_overlapping_bigram_counts(cleaned_text)
        top_5 = bigram_counts.most_common(5)
        print(f"--- Крок 2: 5 найчастіших біграм шифртексту ({filename_to_find}) ---")
        print(f"Успішно прочитано файл: {filepath}\n")
        print("Аналіз біграм, що не перетинаються\n")
        print(" Біграма | Кількість")
        print(" -----------------")
        for bigram, count in top_5:
            print(f" {bigram} | {str(count).ljust(2)}")
    except FileNotFoundError:
        print(f"ПОМИЛКА: Файл '{filename_to_find}' не знайдено.")
        print(f"Я шукав його тут: {filepath}")
        print(f"Будь ласка, переконайтеся, що файл з таким іменем знаходиться в тій же папці, що і скрипт.")
    except Exception as e:
        print(f"Виникла інша помилка: {e}")

if __name__ == "__main__":
    main()