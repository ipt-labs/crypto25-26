import sys
from collections import Counter
from typing import List, Tuple, Dict

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
ALPHABET_SIZE = len(ALPHABET)
RUSSIAN_FREQ = {
    'о': 0.10983, 'е': 0.08483, 'а': 0.07998, 'и': 0.07367,
    'н': 0.06700, 'т': 0.06318, 'с': 0.05473, 'р': 0.04746,
    'в': 0.04533, 'л': 0.04343, 'к': 0.03486, 'м': 0.03203,
    'д': 0.02977, 'п': 0.02804, 'у': 0.02615, 'я': 0.02001,
    'ы': 0.01898, 'ь': 0.01735, 'г': 0.01687, 'з': 0.01641,
    'б': 0.01592, 'ч': 0.01450, 'й': 0.01208, 'х': 0.00966,
    'ж': 0.00940, 'ш': 0.00718, 'ю': 0.00639, 'ц': 0.00486,
    'щ': 0.00361, 'э': 0.00331, 'ф': 0.00267, 'ъ': 0.00037
}

def read_ciphertext(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()    
    cleaned_text = ''.join(content.split()) 
    return cleaned_text.lower()

def compute_coincidence_index(text_segment: str) -> float: #індекс відповідності
    segment_length = len(text_segment)
    if segment_length <= 1:
        return 0.0
    
    char_counts = Counter(text_segment)    
    numerator_sum = sum(count * (count - 1) for count in char_counts.values())
    denominator = segment_length * (segment_length - 1)    
    return numerator_sum / denominator if denominator > 0 else 0.0

def theoretical_index_for_language() -> float:
    return sum(freq ** 2 for freq in RUSSIAN_FREQ.values())

def split_into_blocks(ciphertext: str, block_period: int) -> List[str]:
    blocks = [''] * block_period
    for position, symbol in enumerate(ciphertext):
        blocks[position % block_period] += symbol
    return blocks


def find_period_by_index_method(ciphertext: str, max_period: int = 30) -> int: #М1 через індекс відповідності
    theoretical_value = theoretical_index_for_language()
    random_index = 1.0 / ALPHABET_SIZE
    
    best_period = 1
    best_score = float('inf')
    
    print("\n=== М1: Індекс відповідності блоків ===")
    print(f"Теор. індекс для російської: {theoretical_value:.5f}")
    print(f"Індекс для випадкового тексту: {random_index:.5f}\n")
    
    for period_candidate in range(2, max_period + 1):
        blocks = split_into_blocks(ciphertext, period_candidate)
        
        block_indices = [compute_coincidence_index(block) for block in blocks]
        average_index = sum(block_indices) / len(block_indices)        
        deviation = abs(average_index - theoretical_value) #до теор.        
        print(f"Період {period_candidate:2d}: середній IC = {average_index:.5f}, "
              f"відхилення = {deviation:.5f}")
        
        if deviation < best_score:
            best_score = deviation
            best_period = period_candidate
    
    print(f"\n>>> Найкр. період за м1: {best_period}")
    return best_period


def count_coincidences(ciphertext: str, distance: int) -> int: #к-ть співпадінь
    matches = 0
    text_length = len(ciphertext)
    
    for i in range(text_length - distance):
        if ciphertext[i] == ciphertext[i + distance]:
            matches += 1
    
    return matches


def find_period_by_coincidence_method(ciphertext: str, max_period: int = 30) -> int: #М2 через співпадіння
    print("\n=== М2: Стат. співпадінь Dr ===\n")
    
    coincidence_stats = {}    
    for distance in range(1, max_period + 1):
        coincidences = count_coincidences(ciphertext, distance)
        coincidence_stats[distance] = coincidences
        print(f"D_{distance:2d} = {coincidences:4d}")
    
    sorted_by_value = sorted(coincidence_stats.items(), 
                            key=lambda x: x[1], reverse=True) #лок.макс.
    
    print(f"\nТоп5 відстаней за к-тю співпадінь:")
    for dist, count in sorted_by_value[:5]:
        print(f"  Відстань {dist}: {count} співпадінь")
    
    best_period = sorted_by_value[0][0]
    
    print(f"\n>>> Найкращий період за м2: {best_period}")
    return best_period

def char_to_num(character: str) -> int:
    return ALPHABET.index(character)
def num_to_char(number: int) -> str:
    return ALPHABET[number % ALPHABET_SIZE]





def decrypt_caesar(cipher_block: str, shift_key: int) -> str:
    decrypted = ''
    for symbol in cipher_block:
        if symbol in ALPHABET:
            original_pos = char_to_num(symbol)
            decrypted_pos = (original_pos - shift_key) % ALPHABET_SIZE
            decrypted += num_to_char(decrypted_pos)
        else:
            decrypted += symbol
    return decrypted

def find_most_frequent_char(text_fragment: str) -> str:
    if not text_fragment:
        return ALPHABET[0]
    
    frequency_counter = Counter(text_fragment)
    most_common = frequency_counter.most_common(1)
    return most_common[0][0] if most_common else ALPHABET[0]

def get_most_probable_chars() -> List[str]:
    sorted_chars = sorted(RUSSIAN_FREQ.items(), 
                         key=lambda x: x[1], reverse=True)
    return [char for char, _ in sorted_chars]

def calculate_text_fitness(text: str) -> float: #якість розподілу
    text_length = len(text)
    if text_length == 0:
        return float('inf')
    
    char_counts = Counter(text)
    
    fitness_score = 0.0
    for char, expected_freq in RUSSIAN_FREQ.items():
        actual_count = char_counts.get(char, 0)
        actual_freq = actual_count / text_length
        fitness_score += (actual_freq - expected_freq) ** 2 #через кв.різн.
    return fitness_score

def find_best_key_for_block(cipher_block: str) -> Tuple[int, str]:
    most_frequent_in_block = find_most_frequent_char(cipher_block)
    probable_originals = get_most_probable_chars()[:5]  #топ-5
    
    best_key = 0
    best_decrypted = ''
    best_fitness = float('inf')
    
    for probable_char in probable_originals:        
        key_candidate = (char_to_num(most_frequent_in_block) -     # k=(y-x)modm
                        char_to_num(probable_char)) % ALPHABET_SIZE
        
        decrypted_attempt = decrypt_caesar(cipher_block, key_candidate)
        fitness = calculate_text_fitness(decrypted_attempt)
        if fitness < best_fitness:
            best_fitness = fitness
            best_key = key_candidate
            best_decrypted = decrypted_attempt
    
    return best_key, best_decrypted







def decrypt_vigenere(ciphertext: str, period: int) -> Tuple[str, List[int]]:
    print(f"\n=== Розшифр. з періодом {period} ===\n")
    
    cipher_blocks = split_into_blocks(ciphertext, period)
    found_keys = []
    decrypted_blocks = []
    
    for block_idx, block in enumerate(cipher_blocks):
        key, decrypted_block = find_best_key_for_block(block)
        found_keys.append(key)
        decrypted_blocks.append(decrypted_block)
        
        print(f"Блок {block_idx}: найчаста буква '{find_most_frequent_char(block)}', "
              f"ключ = {key} ('{num_to_char(key)}')")
    
    plaintext = ''
    max_block_length = max(len(block) for block in decrypted_blocks)
    
    for position in range(max_block_length):
        for block_idx in range(period):
            if position < len(decrypted_blocks[block_idx]):
                plaintext += decrypted_blocks[block_idx][position]
    
    return plaintext, found_keys

def manual_key_refinement(ciphertext: str, initial_keys: List[int], 
                         period: int) -> Tuple[str, List[int]]:
    print("\n=== Корек. ключів ===")
    print(f"Поточні ключі: {initial_keys}")
    print(f"Поточний ключ (символи): {''.join(num_to_char(k) for k in initial_keys)}")
    
    refined_keys = initial_keys.copy()
    
    while True:
        user_input = input(f"\nВведіть ключ ({period} симв.) або Enter для пропуску: ").strip().lower()
        
        if user_input == '':
            break
        
        key_clean = ''.join(c for c in user_input if c in ALPHABET)
        
        if len(key_clean) != period:
            print(f"Помилка к-ті символів у ключі: потрібно {period} симв., введено {len(key_clean)}")
            continue
        
        refined_keys = [char_to_num(c) for c in key_clean]        
        blocks = split_into_blocks(ciphertext, period)
        decrypted_blocks = []
        
        for idx, key in enumerate(refined_keys):
            decrypted_blocks.append(decrypt_caesar(blocks[idx], key))
        
        plaintext = ''
        max_len = max(len(b) for b in decrypted_blocks)
        for pos in range(max_len):
            for block_idx in range(period):
                if pos < len(decrypted_blocks[block_idx]):
                    plaintext += decrypted_blocks[block_idx][pos]
        
        print(f"\nКлюч: {key_clean}")
        print(f"Перші 300 симв.:")
        print(plaintext[:300])
        
        save_choice = input("\nЗберегти? (y/n): ").strip().lower()
        if save_choice == 'y':
            return plaintext, refined_keys
    
    blocks = split_into_blocks(ciphertext, period)
    decrypted_blocks = []
    
    for idx, key in enumerate(refined_keys):
        decrypted_blocks.append(decrypt_caesar(blocks[idx], key))

    plaintext = ''
    max_len = max(len(b) for b in decrypted_blocks)
    for pos in range(max_len):
        for block_idx in range(period):
            if pos < len(decrypted_blocks[block_idx]):
                plaintext += decrypted_blocks[block_idx][pos]
    
    return plaintext, refined_keys







def save_result(filename: str, plaintext: str, keys: List[int], period: int):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=== РЕЗУЛЬТАТ ===\n\n")
        f.write(f"Знайд. період: {period}\n")
        f.write(f"Знайд. ключ (числа): {keys}\n")
        f.write(f"Знайд. ключ (текст): {''.join(num_to_char(k) for k in keys)}\n\n")
        f.write("=== РОЗШИФР. ТЕКСТ ===\n\n")
        
        for i in range(0, len(plaintext), 80):
            f.write(plaintext[i:i+80] + '\n')






def main():
    print("=" * 70)
    print("ВАР6")
    print("=" * 70)
    
    cipher_file = 'Text(var.6).txt'
    try:
        ciphertext = read_ciphertext(cipher_file)
        print(f"\nЗавантажено шифртекст: {len(ciphertext)} симв.")
    except FileNotFoundError:
        print(f"Файл сховався),або файл '{cipher_file}' не знайдено!")
        return
    
    cipher_ic = compute_coincidence_index(ciphertext)
    print(f"Індекс відповідності шифртексту: {cipher_ic:.5f}")
    
    # М1
    period_method1 = find_period_by_index_method(ciphertext)
    # М2
    period_method2 = find_period_by_coincidence_method(ciphertext)
    



    print(f"\n{'=' * 70}")
    print(f"Метод 1 дав період: {period_method1}")
    print(f"Метод 2 дав період: {period_method2}")

    final_period = period_method2
    
    print(f"\nВикорист. період: {final_period}")
    print(f"{'=' * 70}")
    
    plaintext, found_keys = decrypt_vigenere(ciphertext, final_period)
    
    print(f"\n{'=' * 70}")
    print("ПОЧАТОК РОЗШИФРОВАНОГО ТЕКСТУ:")
    print(f"{'=' * 70}")
    print(plaintext[:500])#перші 500 симв.
    print("...")
    
    manual_choice = input("\nБажаєте ввести свій ключ? (y/n): ").strip().lower()
    if manual_choice == 'y':
        plaintext, found_keys = manual_key_refinement(ciphertext, found_keys, final_period)
        print(f"\n{'=' * 70}")
        print("ОНОВЛЕНИЙ ТЕКСТ:")
        print(f"{'=' * 70}")
        print(plaintext[:500])
        print("...")
    
    output_file = 'decrypted_var6.txt'
    save_result(output_file, plaintext, found_keys, final_period)
    print(f"\n{'=' * 70}")
    print(f"Результат збер. у файл: {output_file}")
    print(f"{'=' * 70}")
    
    fitness = calculate_text_fitness(plaintext) 
    print(f"\nОцінка якості розшифрування: {fitness:.6f}")
    print("(менше => краще)")


if __name__ == "__main__":
    main()
