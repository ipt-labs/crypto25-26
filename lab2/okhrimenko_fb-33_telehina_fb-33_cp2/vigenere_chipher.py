import os

INPUT_FILE = "cleaned_text.txt"

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
Mod = len(ALPHABET)

LETTER_TO_INDEX = {letter: index for index, letter in enumerate(ALPHABET)}
INDEX_TO_LETTER = {index: letter for index, letter in enumerate(ALPHABET)}


def vigenere_encrypt(plaintext: str, key: str) -> str:
    ciphertext = []
    key_indices = [LETTER_TO_INDEX[k] for k in key]
    key_length = len(key)

    for i, char in enumerate(plaintext):
        if char in LETTER_TO_INDEX:
            p_i = LETTER_TO_INDEX[char]
            k_i = key_indices[i % key_length]

            c_i = (p_i + k_i) % Mod

            ciphertext.append(INDEX_TO_LETTER[c_i])
        else:
            ciphertext.append(char)

    return "".join(ciphertext)


def encrypt_all_keys(input_file: str):

    KEYS = {
        'r=2': 'та',
        'r=3': 'кот',  # cat
        'r=4': 'кава',
        'r=5': 'ключи',
        'r=16': 'криптоанализ',
    }

    if not os.path.exists(input_file):
        print(f" {input_file}")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            plaintext = f.read().strip()

        print(f"Len =  {len(plaintext)}")

        results = {}
        for description, key in KEYS.items():
            print(f"\nEncryption with key: '{key}' (len r={len(key)})")

            ciphertext = vigenere_encrypt(plaintext, key)

            output_filename = f"ciphertext_{description}.txt"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(ciphertext)

            print(f"Save as {output_filename}")
            results[description] = (key, ciphertext)

        return results

    except Exception as e:
        print(f"{e}")
        return None


if __name__ == '__main__':
    encrypt_all_keys(INPUT_FILE)
