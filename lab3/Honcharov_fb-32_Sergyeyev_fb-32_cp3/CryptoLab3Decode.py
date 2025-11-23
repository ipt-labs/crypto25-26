import sys
import re

alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"
m = len(alphabet)
M = m * m         

letter_to_index = {letter: index for index, letter in enumerate(alphabet)}
index_to_letter = {index: letter for index, letter in enumerate(alphabet)}

def extended_euclidean(a, b):
    if b == 0:
        return (a, 1, 0)
    gcd, x1, y1 = extended_euclidean(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return (gcd, x, y)

def mod_inverse(a, m):
    if m == 1:
        return 0
    gcd, x, y = extended_euclidean(a, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def bigram_to_value(bigram, m, local_letter_to_index):
    try:
        x1 = local_letter_to_index[bigram[0]]
        x2 = local_letter_to_index[bigram[1]]
        return x1*m + x2
    except KeyError:
        return None 

def value_to_bigram(value, m, local_index_to_letter):
    try:
        x1 = value // m
        x2 = value % m
        return local_index_to_letter[x1] + local_index_to_letter[x2]
    except KeyError:
        return None

def decrypt_text(ciphertext, a_inv, b_key, m, M, local_alphabet, local_letter_to_index, local_index_to_letter):
    plaintext = ""
    clean_ciphertext = re.sub(f'[^{local_alphabet}]', '', ciphertext.lower())
    
    for i in range(0, len(clean_ciphertext), 2):
        bigram = clean_ciphertext[i:i+2]
        if len(bigram) == 2:
            Y = bigram_to_value(bigram, m, local_letter_to_index)
            if Y is None:
                continue
                
            X = (a_inv * (Y - b_key)) % M
            
            plain_bigram = value_to_bigram(X, m, local_index_to_letter)
            if plain_bigram:
                plaintext += plain_bigram
                
    return plaintext

def main():
    INPUT_FILE = '02.txt'
    KEY_INPUT_FILE = 'keys.txt'
    ALL_OUTPUT_FILE = 'all_decryptions.txt'
    KEYS_TO_TEST = []
    try:
        with open(KEY_INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    a_str, b_str = line.strip().split(',')
                    KEYS_TO_TEST.append((int(a_str), int(b_str)))
        
        if not KEYS_TO_TEST:
            print(f"Помилка: Файл '{KEY_INPUT_FILE}' пустий.", file=sys.stderr)
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"Помилка: Файл ключей '{KEY_INPUT_FILE}' не знайдений.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Загружено {len(KEYS_TO_TEST)} ключей из '{KEY_INPUT_FILE}'.")

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            ciphertext = f.read()
    except FileNotFoundError:
        print(f"Помилка: Файл шифротекста '{INPUT_FILE}' не знайдений.", file=sys.stderr)
        sys.exit(1)

    print(f"Файл '{INPUT_FILE}' успішно прочитан.")
    print(f"Модуль M = {M} (m={m})")
    print(f"Розшифрування... Результати в '{ALL_OUTPUT_FILE}'")
    print("-" * 30)

    try:
        with open(ALL_OUTPUT_FILE, 'w', encoding='utf-8') as f_all:
            for i, (a_key, b_key) in enumerate(KEYS_TO_TEST):
                print(f"#{i+1}: Тестуємо ключ a={a_key}, b={b_key}...")
                f_all.write(f"a={a_key}, b={b_key}\n")
                a_inv = mod_inverse(a_key, M)
                if a_inv is None:
                    print(f"  -> Помилка: Ключ a={a_key} немає оберненого.")
                    f_all.write(f"  -> Помилка: Ключ 'a' немає оберненого за модулем {M}.\n\n") 
                    continue 

                plaintext = decrypt_text(
                    ciphertext, a_inv, b_key, 
                    m, M, alphabet, 
                    letter_to_index, index_to_letter
                )

                f_all.write(plaintext)
                f_all.write("\n")

    except Exception as e:
        print(f"Критична помилка: {e}", file=sys.stderr)

    print("-" * 30)
    print(f"Розшифрування завершено.")

if __name__ == "__main__":
    main()