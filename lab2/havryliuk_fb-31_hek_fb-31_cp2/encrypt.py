import pathlib

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

letter_to_number = {char: index for index, char in enumerate(ALPHABET)}
number_to_letter = {index: char for index, char in enumerate(ALPHABET)}

keys = {
        'key2': "ок",
        'key3': "нет",
        'key4': "ключ",
        'key5': "осень",
        'key10': "терминатор",
        'key16': "командирнесходит"
}


def encrypt(plaintext, key_length, key):
    ciphertext = ""

    # y = (x + k) mod m
    for i in range(len(plaintext)):
        char_num = letter_to_number[plaintext[i]]

        key_char = key[i % key_length]
        k = letter_to_number[key_char]

        c = (char_num + k) % M

        ciphertext += number_to_letter[c]

    return ciphertext


def main():
    with open('filtered_text.txt', 'r', encoding='utf-8') as f:
        plain_text = f.read()

    output_directory = pathlib.Path("ciphertexts")
    output_directory.mkdir(exist_ok=True)

    for name, key_value in keys.items():
        key_length = len(key_value)
        print(f"Encrypting with {name}...")
        output_filename = f"ciphertext_{name}.txt"
        full_path = output_directory / output_filename

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(encrypt(plain_text, key_length, key_value))

        print(f"Results saved in {full_path}")


if __name__ == "__main__":
    main()