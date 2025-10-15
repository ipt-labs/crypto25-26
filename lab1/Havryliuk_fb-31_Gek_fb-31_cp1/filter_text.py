ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
INPUT_FILE = "TEXT.txt"
OUTPUT_FILE = "filtered_text.txt"

print(f"Reading file '{INPUT_FILE}'...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    original_text = f.read()

lowered_text = original_text.lower()

filtered_chars = []
for char in lowered_text:
        if char in ALPHABET:
            filtered_chars.append(char)
        else:
            filtered_chars.append(' ')

text_with_many_spaces = "".join(filtered_chars)

words = text_with_many_spaces.split()
processed_text = ' '.join(words)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as file_out:
    file_out.write(processed_text)

print(f"Filtered text is saved to '{OUTPUT_FILE}'")