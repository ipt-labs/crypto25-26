import matplotlib.pyplot as plt
from collections import Counter
import sys
import math
sys.stdout.reconfigure(encoding='utf-8')
letters = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
letters_len = len(letters)

let_freq = {
    'о': 0.10983, 'е': 0.08483, 'а': 0.07998, 'и': 0.07367, 'н': 0.06700,'т': 0.06318, 
    'с': 0.05473, 'р': 0.04746, 'в': 0.04533, 'л': 0.04343,'к': 0.03486, 'м': 0.03203, 
    'д': 0.02977, 'п': 0.02804, 'у': 0.02615,'я': 0.02001, 'ы': 0.01898, 'ь': 0.01735, 
    'г': 0.01687, 'з': 0.01641,'б': 0.01592, 'ч': 0.01450, 'х': 0.01208, 'ж': 0.00940, 
    'й': 0.00752, 'ш': 0.00718, 'ю': 0.00639, 'ц': 0.00486,'щ': 0.00361,'э': 0.00331, 
    'ф': 0.00267, 'ъ': 0.00037
}
def clean_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().replace('ё', 'е').replace('\n', '').lower()
            content = ''.join(c for c in content if c in letters)
        return content
    except FileNotFoundError:
        print(f"Помилка: Файл не знайдено")
        return ""

def index_of_coincidence(segment):
    length = len(segment)
    if length < 2:
        return 0
    counts = Counter(segment)
    return sum(v * (v - 1) for v in counts.values()) / (length * (length - 1))

def split_text(text, key_len):
    return [''.join(text[i::key_len]) for i in range(key_len)]

def avg_ic(text, max_key_len):
    ic_summary = []
    for k_len in range(2, max_key_len + 1):
        blocks = split_text(text, k_len)
        ic_block_values = [index_of_coincidence(block) for block in blocks if block]
        if ic_block_values:
            avg_ic_value = sum(ic_block_values) / len(ic_block_values)
            ic_summary.append((k_len, avg_ic_value))
    return ic_summary

def plot_ic(data):   
    if not data:
        return
    key_lengths, ic_values = zip(*data)
    plt.figure(figsize=(10,6))
    plt.plot(key_lengths, ic_values, marker='o', linestyle='-', color='teal', label='Середній IC')
    
    plt.title('Середній індекс відповідності для різних довжин ключа')
    plt.xlabel('Довжина ключа (k)')
    plt.ylabel('IC')
    plt.xticks(key_lengths)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.show()

def find_vigenere_key(cipher_text, key_len):
    blocks = split_text(cipher_text, key_len)
    key = []
    expected_freq = [let_freq.get(letter, 0) for letter in letters]
    for block in blocks:
        if len(block) < 20:
            key.append(letters[0])
            continue
        counts = Counter(block)
        best_shift = min(
            range(letters_len),
            key=lambda shift: sum(
                ((counts.get(letters[(i + shift) % letters_len], 0) - len(block) * expected_freq[i]) ** 2)
                / (len(block) * expected_freq[i]) if expected_freq[i] > 0 else 0
                for i in range(letters_len)
            )
        )
        key.append(letters[best_shift])

    return ''.join(key)


def decrypt_vigenere(cipher_text, key):
    decrypted_text = []
    key_len = len(key)
    for i, char in enumerate(cipher_text):
        if char in letters:
            k_index = letters.index(key[i % key_len])
            c_index = letters.index(char)
            decrypted_text.append(letters[(c_index - k_index) % letters_len])
        else:
            decrypted_text.append(char)
    return ''.join(decrypted_text)

if __name__ == "__main__":
    file_path = "lab2_3.txt"
    text_data = clean_file(file_path)        
    max_len = 25
    ic_results = avg_ic(text_data, max_len)
    plot_ic(ic_results)
    best_length = max(ic_results, key=lambda x: x[1])[0] if ic_results else 3 
    print("-" * 50)
    print(f"Найбільш ймовірна довжина ключа: {best_length}")
    key = find_vigenere_key(text_data, best_length)
    print(f"Знайдений ключ: {key}")
    decrypted_text = decrypt_vigenere(text_data, key)
    output_file = 'decrypted.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decrypted_text)
    print("Перші 200 символів розшифрованого тексту:")
    print(decrypted_text[:200])
