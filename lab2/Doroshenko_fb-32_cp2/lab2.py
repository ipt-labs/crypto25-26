import collections
import re
import os
import matplotlib.pyplot as plt


ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)
CHAR_TO_INDEX = {char: i for i, char in enumerate(ALPHABET)}
INDEX_TO_CHAR = {i: char for i, char in enumerate(ALPHABET)}

# Очищення тексту
def clean_text(text):
    text = text.lower().replace('ё', 'е')
    cleaned = "".join(re.findall(f"[{ALPHABET}]", text))
    return cleaned

# Шифрування Віженера
def vigenere_encrypt(plain_text, key):
    cipher_text = []
    key = clean_text(key)
    key_indices = [CHAR_TO_INDEX[k] for k in key]
    r = len(key)
    for i, char in enumerate(plain_text):
        x_i = CHAR_TO_INDEX[char]
        k_i = key_indices[i % r]
        y_i = (x_i + k_i) % M
        cipher_text.append(INDEX_TO_CHAR[y_i])
    return "".join(cipher_text)

# Розрахунок індексу відповідності
def index_of_coincidence(text):
    n = len(text)
    if n <= 1: return 0
    counts = collections.Counter(text)
    sum_nt = sum(count * (count - 1) for count in counts.values())
    return sum_nt / (n * (n - 1))

def main():
    input_file = 'lab2/Doroshenko_fb-32_cp2/task1.txt'
    output_file = 'lab2/Doroshenko_fb-32_cp2/task1_encrypted.txt'

    if not os.path.exists(input_file):
        print(f"Помилка: Файл {input_file} не знайдено!")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = f.read()

    plain_text = clean_text(raw_data)
    print(f"Текст зчитано. Довжина після очищення: {len(plain_text)} симв.\n")

    # Набір ключів
    keys = ["да", "три", "небо", "экран", "криптография", "алгоритмышифрования", "программнаяинженерия"]

    results = [("Відкритий текст", "-", "-", index_of_coincidence(plain_text))]
    ciphertexts_data = [] # Для запису у файл

    # Списки для діаграми
    plot_labels = ["Відкритий"]
    plot_values = [results[0][3]]

    for key in keys:
        encrypted = vigenere_encrypt(plain_text, key)
        ic = index_of_coincidence(encrypted)
        r_len = len(key)

        results.append((f"Шифртекст r={r_len}", key, r_len, ic))
        ciphertexts_data.append((key, r_len, encrypted))

        plot_labels.append(f"r={r_len}")
        plot_values.append(ic)

    # Вивід таблиці в консоль
    print(f"{'Тип тексту':<22} | {'Ключ':<22} | {'r':<4} | {'Індекс (I)'}")
    print("-" * 75)
    for label, key, r, ic in results:
        print(f"{label:<22} | {key:<22} | {str(r):<4} | {ic:.5f}")

    # Збереження діаграми
    plt.figure(figsize=(10, 6))
    plt.bar(plot_labels, plot_values, color='skyblue', edgecolor='navy')
    plt.ylabel('Індекс відповідності (I)')
    plt.title('Порівняння індексів відповідності')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('lab2/Doroshenko_fb-32_cp2/ic_comparison.png')
    print("\nДіаграму збережено у файл 'ic_comparison.png'")

    # Запис усіх шифртекстів у файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("РЕЗУЛЬТАТИ ШИФРУВАННЯ\n")
        f.write("="*50 + "\n\n")
        for key, r, text in ciphertexts_data:
            f.write(f"Ключ: {key} (довжина r={r})\n")
            f.write("-" * 30 + "\n")
            f.write(text + "\n")
            f.write("-" * 30 + "\n\n")

    print(f"Усі шифртексти збережено у файл '{output_file}'")

if __name__ == "__main__":
    main()
