import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
ALPHABET_SIZE = len(ALPHABET)

LANGUAGE_FREQUENCIES = {
    'о': 0.1037871035, 'и': 0.0867394604, 'е': 0.0878555126, 'а': 0.0829055014,
    'с': 0.0495496985, 'т': 0.0635783234, 'н': 0.0643695491, 'в': 0.0479794641,
    'л': 0.0488842353, 'р': 0.0412393138, 'д': 0.0314535556, 'м': 0.0337172802,
    'п': 0.0256325493, 'к': 0.0261693755, 'у': 0.0282879343, 'г': 0.0169161315,
    'я': 0.0198431634, 'ы': 0.0207939278, 'б': 0.0174852966, 'з': 0.0168952909,
    'ь': 0.0148809353, 'х': 0.0163670885, 'ч': 0.0103462996, 'й': 0.0096944906,
    'ж': 0.0098928360, 'ш': 0.0067753638, 'ю': 0.0072935052, 'ц': 0.0020114810,
    'щ': 0.0054674340, 'ф': 0.0004405280, 'э': 0.0027473712, 'ъ': 0.0001
}

THEORETICAL_IC = sum(p**2 for p in LANGUAGE_FREQUENCIES.values())

def calculate_ic(text):
    text_len = len(text)
    if text_len <= 1:
        return 0
    
    freqs = Counter(text)
    numerator = sum(f * (f - 1) for f in freqs.values())
    denominator = text_len * (text_len - 1)
    
    return numerator / denominator

def split_text_into_blocks(text, num_blocks):
    blocks = ['' for _ in range(num_blocks)]
    for i, char in enumerate(text):
        blocks[i % num_blocks] += char
    return blocks

def find_best_shift(block):
    best_shift_char = 0
    max_correlation = -1
    block_len = len(block)
    
    char_indices = [ALPHABET.index(c) for c in block]

    for shift in range(ALPHABET_SIZE):
        shifted_counts = [0] * ALPHABET_SIZE
        for index in char_indices:
            shifted_index = (index - shift) % ALPHABET_SIZE
            shifted_counts[shifted_index] += 1
        
        correlation = sum((shifted_counts[i] / block_len) * LANGUAGE_FREQUENCIES.get(ALPHABET[i], 0) for i in range(ALPHABET_SIZE))
        
        if correlation > max_correlation:
            max_correlation = correlation
            best_shift_char = shift
            
    return best_shift_char

def decrypt_vigenere(ciphertext, key):
    key_indices = [ALPHABET.index(c) for c in key]
    key_len = len(key)
    result = []
    
    for i, char in enumerate(ciphertext):
        char_index = ALPHABET.index(char)
        decrypted_index = (char_index - key_indices[i % key_len]) % ALPHABET_SIZE
        result.append(ALPHABET[decrypted_index])
        
    return ''.join(result)

def create_plot(x_values, y_values, target_ic, output_filename):
    plt.figure(figsize=(12, 6))
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.bar(x_values, y_values, color='pink', label='Середній IC для довжини ключа')
    plt.axhline(y=target_ic, color='crimson', linestyle='--', label=f'Теоретичний IC ({target_ic:.4f})')
    
    plt.xlabel("Довжина ключа (r)")
    plt.ylabel("Середній індекс відповідності")
    plt.title("Пошук довжини ключа методом індексу відповідності")
    plt.xticks(x_values)
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()

def main():
    input_filename = input("Введіть назву файлу з шифротекстом: ")
    decrypted_filename = "decrypted_text.txt"
    plot_filename = "ic_analysis_plot.png"
    
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            ciphertext = ''.join(filter(lambda char: char in ALPHABET, f.read().lower()))
    except FileNotFoundError:
        print(f"Помилка: Файл '{input_filename}' не знайдено.")
        return

    probable_key_length = 0
    min_diff = float('inf')
    
    r_values = []
    avg_ic_values = []

    print("\nАналіз довжини ключа:")
    print("-" * 25)
    print("Довжина (r)\tСередній IC")
    print("-" * 25)

    for r in range(2, 31):
        blocks = split_text_into_blocks(ciphertext, r)
        avg_ic = sum(calculate_ic(b) for b in blocks) / r
        
        diff = abs(avg_ic - THEORETICAL_IC)
        if diff < min_diff:
            min_diff = diff
            probable_key_length = r
            
        print(f"{r}\t\t{avg_ic:.5f}")
        r_values.append(r)
        avg_ic_values.append(avg_ic)

    print("-" * 25)
    print(f"Ймовірна довжина ключа: {probable_key_length}")

    key_blocks = split_text_into_blocks(ciphertext, probable_key_length)
    recovered_key = ''.join(ALPHABET[find_best_shift(block)] for block in key_blocks)
    print(f"Відновлений ключ: {recovered_key}\n")

    decrypted_text = decrypt_vigenere(ciphertext, recovered_key)
    
    try:
        with open(decrypted_filename, "w", encoding="utf-8") as f:
            f.write(f"Відновлений ключ: {recovered_key}\n\n")
            f.write(decrypted_text)
        print(f"Дешифрований текст збережено у файл: {decrypted_filename}")
    except IOError:
        print(f"Помилка: Не вдалося записати файл '{decrypted_filename}'.")

    create_plot(r_values, avg_ic_values, THEORETICAL_IC, plot_filename)
    print(f"Графік аналізу збережено у файл: {plot_filename}")

if __name__ == "__main__":
    main()
