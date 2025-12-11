import sys
from collections import Counter

FILENAME = 'var_3.txt'
ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
MOST_FREQ_CHAR = 'о'


def load_text(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Файл '{filename}' не знайдено.")
        sys.exit(1)
    except Exception as e:
        print(f"Помилка під час читання файлу: {e}")
        sys.exit(1)


def clean_text(text, alphabet):
    return "".join([c for c in text.lower() if c in alphabet])


def find_key(cleaned_text, key_length, alphabet, most_freq_char):
    print(f"\n--- Пошук ключа довжиною {key_length} ---")

    m = len(alphabet)
    found_key = ""

    expected_freq_idx = alphabet.find(most_freq_char)

    if expected_freq_idx == -1:
        print(
            f"ПОМИЛКА: Найчастіший символ '{most_freq_char}' не знайдено в алфавіті.")
        sys.exit(1)

    print(
        f"Припущення: найчастіша літера відкритого тексту - '{most_freq_char}' (індекс {expected_freq_idx}).\n")

    for i in range(key_length):

        column_text = cleaned_text[i::key_length]

        if not column_text:
            print(f"Увага: Колонка {i+1} порожня.")
            found_key += "?"
            continue

        freq_analysis = Counter(column_text)
        most_common_char_in_col, _ = freq_analysis.most_common(1)[0]

        y_idx = alphabet.find(most_common_char_in_col)
        x_idx = expected_freq_idx
        k_idx = (y_idx - x_idx) % m

        key_letter = alphabet[k_idx]
        found_key += key_letter

        print(
            f"Колонка {i+1:2}: найчастіша літера '{most_common_char_in_col}' (індекс {y_idx}).")
        print(
            f"          Розрахунок: k_idx = ({y_idx} - {x_idx}) mod {m} = {k_idx}. ")
        print(f"          Знайдена літера ключа: '{key_letter}'\n")

    return found_key


def decrypt(original_text, key, alphabet):
    m = len(alphabet)
    key_len = len(key)
    key_indices = [alphabet.find(k) for k in key]

    decrypted_text = ""
    key_index = 0

    for char in original_text:
        char_low = char.lower()

        if char_low in alphabet:
            k_idx = key_indices[key_index]
            y_idx = alphabet.find(char_low)

            x_idx = (y_idx - k_idx) % m
            dec_char = alphabet[x_idx]

            if char.isupper():
                decrypted_text += dec_char.upper()
            else:
                decrypted_text += dec_char

            key_index = (key_index + 1) % key_len
        else:
            decrypted_text += char

    return decrypted_text


def main():

    original_text = load_text(FILENAME)
    cleaned_text = clean_text(original_text, ALPHABET)

    key_length = 14

    key = find_key(cleaned_text, key_length, ALPHABET, MOST_FREQ_CHAR)

    print(f"Ймовірний ключ знайдено: {key}")

    decrypted_text = decrypt(original_text, key, ALPHABET)

    print("\n--- РЕЗУЛЬТАТ РОЗШИФРОВКИ ---")
    print(decrypted_text)


if __name__ == "__main__":
    main()
