import collections
import os
import sys
import matplotlib.pyplot as plt

result_dir = "results"
ciphertext_file = "cipher.txt"
decrypted_file = "decryptedtext.txt"
dr_plot_file = "analysisDr.png"
max_r_to_check = 30 
alphabet_start = 'а'
alphabet_size = 32

russian_frequencies = {
    'о': 0.10983, 'е': 0.08483, 'а': 0.07998, 'и': 0.07367, 'н': 0.06700,
    'т': 0.06318, 'с': 0.05473, 'р': 0.04746, 'в': 0.04533, 'л': 0.04343,
    'к': 0.03486, 'м': 0.03203, 'д': 0.02977, 'п': 0.02804, 'у': 0.02615,
    'я': 0.02001, 'ы': 0.01898, 'ь': 0.01735, 'г': 0.01685, 'з': 0.01641,
    'б': 0.01592, 'ч': 0.01450, 'й': 0.01208, 'х': 0.00966, 'ж': 0.00940,
    'ш': 0.00718, 'ю': 0.00639, 'ц': 0.00486, 'щ': 0.00361, 'э': 0.00331,
    'ф': 0.00267, 'ъ': 0.00037
}

def calculate_ic(text: str) -> float:
    n = len(text)
    if n <= 1: return 0.0
    frequencies = collections.Counter(text)
    num = sum(val * (val - 1) for val in frequencies.values())
    den = float(n * (n - 1))
    return num / den

def get_average_ic_for_r(text: str, r: int) -> float:
    blocks = [""] * r
    for i, char in enumerate(text):
        blocks[i % r] += char
    total_ic = sum(calculate_ic(block) for block in blocks if block)
    return total_ic / r

def get_dr_statistic(text: str, r: int) -> int:
    n = len(text)
    matches = 0
    for i in range(n - r):
        if text[i] == text[i+r]:
            matches += 1
    return matches

def find_best_key_length(text: str, max_r: int) -> int:
    ic_results = {}
    for r in range(2, max_r + 1):
        ic_results[r] = get_average_ic_for_r(text, r)
    best_r = max(ic_results, key=ic_results.get)
    return best_r

def find_key_letter_for_block(block: str) -> str:
    if not block:
        return "?"
        
    best_shift = 0
    max_correlation = -1.0
    block_len = len(block)
    
    for shift in range(alphabet_size):
        correlation = 0.0
        block_freqs = collections.Counter()
        
        for char in block:
            c_index = ord(char) - ord(alphabet_start)
            p_index = (c_index - shift + alphabet_size) % alphabet_size
            block_freqs[chr(p_index + ord(alphabet_start))] += 1
            
        for char_code in range(alphabet_size):
            char = chr(char_code + ord(alphabet_start))
            f_i = block_freqs[char] / block_len
            p_i = russian_frequencies.get(char, 0.0)
            correlation += f_i * p_i
            
        if correlation > max_correlation:
            max_correlation = correlation
            best_shift = shift
            
    return chr(best_shift + ord(alphabet_start))

def find_key(text: str, r: int) -> str:
    key = ""
    blocks = [""] * r
    for i, char in enumerate(text):
        blocks[i % r] += char
        
    for block in blocks:
        key += find_key_letter_for_block(block)
        
    return key

def vigenere_decrypt(text: str, key: str) -> str:
    decrypted_text = ""
    key_len = len(key)
    if key_len == 0:
        return "Помилка: ключ порожній."
        
    for i, char in enumerate(text):
        c_index = ord(char) - ord(alphabet_start)
        k_index = ord(key[i % key_len]) - ord(alphabet_start)
        p_index = (c_index - k_index + alphabet_size) % alphabet_size
        decrypted_text += chr(p_index + ord(alphabet_start))
        
    return decrypted_text

def main():
    os.makedirs(result_dir, exist_ok=True)
    
    try:
        with open(ciphertext_file, 'r', encoding='utf-8') as f:
            ciphertext = f.read().replace('\n', '')
    except FileNotFoundError:
        print(f"Помилка: файл '{ciphertext_file}' не знайдено.")
        sys.exit(1)
        
    if not ciphertext:
        print(f"Помилка: файл '{ciphertext_file}' порожній.")
        sys.exit(1)

    best_r = find_best_key_length(ciphertext, max_r_to_check)
    found_key = find_key(ciphertext, best_r)
    decrypted_text = vigenere_decrypt(ciphertext, found_key)
    
    print("\nАналіз Dr для побудови діаграми...")
    r_values = list(range(2, max_r_to_check + 1))
    dr_values = [get_dr_statistic(ciphertext, r) for r in r_values]
    print("Аналіз Dr завершено")
    
    dr_plot_path = os.path.join(result_dir, dr_plot_file)
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(r_values, dr_values, marker='.', linestyle='-')
        plt.title('Кількість збігів в залежності від r (Метод Dr)')
        plt.xlabel('r (потенційна довжина ключа)')
        plt.ylabel('Кількість збігів (Dr)')
        plt.xticks(list(range(5, max_r_to_check + 1, 5)))
        plt.grid(True, linestyle=':')
        plt.savefig(dr_plot_path)
        print(f"Діаграму Dr збережено у: {dr_plot_path}")
    except Exception as e:
        print(f"Помилка при створенні діаграми Dr: {e}")

    decrypted_path = os.path.join(result_dir, decrypted_file)
    with open(decrypted_path, 'w', encoding='utf-8') as f:
        f.write(decrypted_text)

    print(f" Використовуваний період ключа (r): {best_r}")
    print(f" Знайдений ключ: {found_key.upper()} (Довжина {len(found_key)})")
    print(f" Розшифрований текст:")
    print(decrypted_text)
    print(f"\nРозшифрований текст збережено у: {decrypted_path}\n")

if __name__ == "__main__":
    main()