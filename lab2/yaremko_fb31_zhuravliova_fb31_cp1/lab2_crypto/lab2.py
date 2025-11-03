import sys
from collections import Counter

FILENAME = 'var_3.txt'
ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
MOST_FREQ_CHAR = 'о'
MAX_KEY_LENGTH = 30


def load_text(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error while reading file: {e}")
        sys.exit(1)


def clean_text(text, alphabet):
    return "".join([c for c in text.lower() if c in alphabet])


def decrypt(original_text, key, alphabet):
    print("\n--- 3. Decrypting text ---")
    m = len(alphabet)
    key_len = len(key)
    key_indices = [alphabet.find(k) for k in key]

    decrypted_text = ""
    key_index = 0

    for char in original_text:
        char_low = char.lower()

        if char_low in alphabet:
            # Decrypt the letter
            k_idx = key_indices[key_index]
            y_idx = alphabet.find(char_low)

            # Decryption formula: x_idx = (y_idx - k_idx) mod m
            x_idx = (y_idx - k_idx) % m

            dec_char = alphabet[x_idx]

            # Restore original case
            if char.isupper():
                decrypted_text += dec_char.upper()
            else:
                decrypted_text += dec_char

            # Move to next key letter
            key_index = (key_index + 1) % key_len

        else:
            # Keep non-letter characters as they are
            decrypted_text += char

    return decrypted_text


def main():
    original_text = load_text(FILENAME)

    key_length = 14
    print(f"Key length set to: {key_length}")

    MANUAL_KEY = 'экомаятникфуко'

    key = MANUAL_KEY.lower()
    if not all(c in ALPHABET for c in key):
        print(
            f"ERROR: Key '{key}' contains characters not present in the alphabet.")
        return

    if len(key) != key_length:
        print(
            f"ERROR: Key length '{len(key)}' does not match the expected length ({key_length}).")
        return

    print(f"\nUsing manually entered key: '{key}'")

    decrypted_text = decrypt(original_text, key, ALPHABET)

    print("\n--- DECRYPTION RESULT ---")
    print(decrypted_text)


if __name__ == "__main__":
    main()
