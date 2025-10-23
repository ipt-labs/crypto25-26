import collections
import matplotlib.pyplot as plt
import re
import sys

RUSSIAN_ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

RUSSIAN_FREQUENCIES = {
    'о': 0.10983, 'е': 0.08483, 'а': 0.07998, 'и': 0.07367, 'н': 0.067,
    'т': 0.06318, 'с': 0.05473, 'р': 0.04746, 'в': 0.04533, 'л': 0.04343,
    'к': 0.03486, 'м': 0.03203, 'д': 0.02977, 'п': 0.02804, 'у': 0.02615,
    'я': 0.02001, 'ы': 0.01898, 'ь': 0.01735, 'г': 0.01687, 'з': 0.01641,
    'б': 0.01592, 'ч': 0.0145,  'й': 0.01208, 'х': 0.00966, 'ж': 0.0094,
    'ш': 0.00718, 'ю': 0.00639, 'ц': 0.00486, 'щ': 0.00361, 'э': 0.00331,
    'ф': 0.00267, 'ъ': 0.00037
}

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = text.replace('ё', 'е')
    cleaned_text = re.sub(f'[^%s]' % RUSSIAN_ALPHABET, '', text)
    return cleaned_text

def get_index_of_coincidence(text):
    n = len(text)
    if n < 2:
        return 0.0
    
    counts = collections.Counter(text)
    index = sum(count * (count - 1) for count in counts.values())
    return index / (n * (n - 1))

key_IC = {}

def find_key_length(ciphertext, min_len=2, max_len=30):
    print(f"--- Етап 1: Пошук довжини ключа (r) ---")
    best_len = 0
    max_avg_ic = 1.0 / len(RUSSIAN_ALPHABET) 

    for key_len in range(min_len, max_len + 1):
        total_ic = 0.0
        for i in range(key_len):
            sub_text = ciphertext[i::key_len]
            if len(sub_text) > 1:
                total_ic += get_index_of_coincidence(sub_text)
        
        avg_ic = total_ic / key_len
        key_IC[key_len] = avg_ic
        print(f"r = {key_len:2d}: {avg_ic:.6f}")
        
        if avg_ic > max_avg_ic:
            max_avg_ic = avg_ic
            best_len = key_len
            
    print("-" * 30)
    return best_len

def find_key(ciphertext, key_length):
    print(f"\n--- Етап 2: Пошук ключа довжиною r = {key_length} ---")
    key = ''
    
    for i in range(key_length):
        sub_text = ciphertext[i::key_length]
        if not sub_text:
            continue

        best_shift = 0
        max_corr = -1.0
        
        for shift in range(len(RUSSIAN_ALPHABET)):
            shifted_text = ''
            for char in sub_text:
                shifted_index = (RUSSIAN_ALPHABET.find(char) - shift + len(RUSSIAN_ALPHABET)) % len(RUSSIAN_ALPHABET)
                shifted_text += RUSSIAN_ALPHABET[shifted_index]
            
            counts = collections.Counter(shifted_text)
            n = len(shifted_text)
            
            current_corr = 0.0
            if n > 0:
                current_corr = sum(counts.get(char, 0) / n * RUSSIAN_FREQUENCIES.get(char, 0) for char in RUSSIAN_ALPHABET)

            if current_corr > max_corr:
                max_corr = current_corr
                best_shift = shift
        
        key_char = RUSSIAN_ALPHABET[best_shift]
        print(f"Блок {i:2d}: Знайдена літера ключа = '{key_char}'")
        key += key_char
        
    print("-" * 30)
    return key

def decrypt_vigenere(ciphertext, key):
    plaintext = ''
    key_index = 0
    if not key:
        return "Помилка: Ключ порожній."

    for char in ciphertext:
        if char not in RUSSIAN_ALPHABET:
            continue
            
        key_char = key[key_index % len(key)]
        shift = RUSSIAN_ALPHABET.find(key_char)
        
        decrypted_index = (RUSSIAN_ALPHABET.find(char) - shift + len(RUSSIAN_ALPHABET)) % len(RUSSIAN_ALPHABET)
        plaintext += RUSSIAN_ALPHABET[decrypted_index]
        key_index += 1
        
    return plaintext

def main():
    filename = r"F:\sem5\crypt\lab2\lab2\var5.txt" 
    
    output_filename = "F:\sem5\crypt\lab2\lab2\decrypted_var5.txt"

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            raw_encrypted_text = f.read()
    except FileNotFoundError:
        print(f"ПОМИЛКА: Файл '{filename}' не знайдено.")
        print("Будь ласка, перевірте шлях до файлу 'filename' у коді.")
        sys.exit(1)
        
    encrypted_text = preprocess_text(raw_encrypted_text)
    print(f"Довжина очищеного шифртексту: {len(encrypted_text)} символів\n")
    if not encrypted_text:
        print("ПОМИЛКА: Файл порожній або не містить потрібних літер.")
        sys.exit(1)

    key_length = find_key_length(encrypted_text, max_len=30)
    if key_length == 0:
        print("Не вдалося знайти імовірну довжину ключа. Завершення роботи.")
        sys.exit(1)
        
    print(f"-> Ймовірна довжина ключа: {key_length}")

    plt.figure(figsize=(10,6))
    plt.bar(key_IC.keys(), key_IC.values(), color="skyblue", edgecolor="black")
    plt.axhline(y=0.055, color='r', linestyle='--', label='IC Російської мови (~0.055)')
    plt.axhline(y=(1/32), color='g', linestyle='--', label='IC Випадковий (~0.031)')
    plt.xlabel("Довжина ключа (r)", fontsize=12)
    plt.ylabel("Середній Індекс Відповідності (IC)", fontsize=12)
    plt.title("Аналіз індексу відповідності для довжини ключа", fontsize=14)
    plt.xticks(list(key_IC.keys()))
    plt.legend()
    plt.tight_layout()
    plt.show()

    found_key = find_key(encrypted_text, key_length)
    print(f"-> Знайдений ключ: {found_key}")

    decrypted_text = decrypt_vigenere(encrypted_text, found_key)

    print(f"\n--- Етап 3: Розшифрований текст ---")
    print(decrypted_text[:1500] + "...")

    try:
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            f_out.write(decrypted_text)
        print(f"\n[ГОТОВО] Повний розшифрований текст збережено у файл:")
        print(f"{output_filename}")
    except IOError as e:
        print(f" !! Помилка збереження файлу: {e}")

if __name__ == "__main__":
    main()