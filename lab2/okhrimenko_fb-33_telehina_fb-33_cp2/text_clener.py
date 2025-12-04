import re
import os


def clean_text_for_vigenere(text):
    text = text.lower()
    text = text.replace('ё', 'е')
    cleaned_text = re.sub(r'[^а-я]', '', text)

    return cleaned_text


def process_file(input_filename="text3.txt", output_filename="cleaned_text3.txt"):

    if not os.path.exists(input_filename):
        print(f"Error '{input_filename}' no file ")
        return

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        cleaned_text = clean_text_for_vigenere(raw_text)

        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        print("-" * 40)
        print(f"Save in: {output_filename}")
        print(f"Len of cleaned text : {len(cleaned_text)}")
        print("-" * 40)

        print(cleaned_text[:100] + ('...' if len(cleaned_text) > 100 else ''))

    except Exception as e:
        print(f"error {e}")


if __name__ == "__main__":
    process_file()
