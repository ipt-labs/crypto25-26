import collections
import matplotlib.pyplot as plt
import numpy as np

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
ALPHABET_SIZE = len(ALPHABET)
""""Значення взяті з результатів 1 лабораторної роботи"""
RUSSIAN_LETTER_FREQUENCIES = {
    'о': 0.11225, 'е': 0.083863, 'а': 0.07878, 'и': 0.068856, 'н': 0.061797,
    'т': 0.060067, 'с': 0.051117, 'р': 0.042043, 'в': 0.04693, 'л': 0.045547,
    'к': 0.040772, 'м': 0.029608, 'д': 0.031081, 'п': 0.027842, 'у': 0.030343,
    'я': 0.019733, 'ы': 0.019331, 'ь': 0.020383, 'г': 0.018083, 'з': 0.016891,
    'б': 0.019047, 'ч': 0.017904, 'й': 0.010469, 'х': 0.009821, 'ж': 0.010836,
    'ш': 0.009751, 'ю': 0.006278, 'ц': 0.003847, 'щ': 0.002926, 'э': 0.00219,
    'ф': 0.001217, 'ъ': 0.000286
}

def load_and_clean_ciphertext(filename="text.txt"):
    with open(filename, 'r', encoding='utf-8') as file:
        return ''.join(char for char in file.read().lower() if char in ALPHABET)

def calculate_ioc(text: str) -> float:
    """Обчислює індекс відповідності для заданого тексту"""
    text_length = len(text)
    if text_length < 2:
        return 0.0
    frequencies = collections.Counter(text)
    ioc_sum = sum(count * (count - 1) for count in frequencies.values())
    return ioc_sum / (text_length * (text_length - 1))

def find_key_length(ciphertext: str, max_key_length: int = 30):
    """Визначає довжину ключа за допомогою аналізу індексу відповідності"""
    possible_key_lengths = range(2, max_key_length + 1)
    average_iocs = []

    for key_length in possible_key_lengths:
        columns = [''.join(ciphertext[i::key_length]) for i in range(key_length)]
        iocs_for_columns = [calculate_ioc(col) for col in columns]
        average_ioc = np.mean(iocs_for_columns)
        average_iocs.append(average_ioc)
        print(f"Довжина ключа {key_length:2}: Середній IoC = {average_ioc:.4f}")

    plt.figure(figsize=(12, 6))
    plt.plot(possible_key_lengths, average_iocs, marker='o')
    plt.title('Аналіз довжини ключа за індексом відповідності')
    plt.xlabel('Довжина ключа')
    plt.ylabel('Середній індекс відповідності')
    plt.xticks(possible_key_lengths)
    plt.grid(True)
    plt.show()

    best_length = max(range(len(average_iocs)), key=average_iocs.__getitem__) + 2
    print(f"\nНайбільш імовірна довжина ключа: {best_length}")
    return best_length
    
def find_vigenere_key(ciphertext: str, key_length: int) -> str:
    """Знаходить ключ, порівнюючи частоти літер у колонках з еталонними(з 1 лабораторної)"""
    found_key = ''
    standard_frequencies_vector = np.array([RUSSIAN_LETTER_FREQUENCIES[char] for char in ALPHABET])

    for i in range(key_length):
        column_text = ciphertext[i::key_length]
        best_shift = 0
        max_correlation = -1

        for shift in range(ALPHABET_SIZE):
            decrypted_column = ''.join(ALPHABET[(ALPHABET.index(char) - shift) % ALPHABET_SIZE] for char in column_text)
            segment_frequencies = collections.Counter(decrypted_column)
            total_chars = len(decrypted_column)
            segment_probabilities_vector = np.array([segment_frequencies.get(char, 0) / total_chars for char in ALPHABET])
            correlation = np.dot(segment_probabilities_vector, standard_frequencies_vector)
            if correlation > max_correlation:
                max_correlation = correlation
                best_shift = shift
        found_key += ALPHABET[best_shift]       
    print(f"Знайдений ключ: {found_key}")
    return found_key

def vigenere_decrypt(ciphertext: str, key: str) -> str:
    plaintext = ''
    key_length = len(key)  
    for i, char in enumerate(ciphertext):
        key_char = key[i % key_length]
        plain_char_index = (ALPHABET.index(char) - ALPHABET.index(key_char)) % ALPHABET_SIZE
        plaintext += ALPHABET[plain_char_index]      
    return plaintext

if __name__ == "__main__":
    ciphertext_from_file = load_and_clean_ciphertext()
    best_key_length = find_key_length(ciphertext_from_file)  
    final_key = find_vigenere_key(ciphertext_from_file, best_key_length)  
    decrypted_text = vigenere_decrypt(ciphertext_from_file, final_key)
    print(f"\nРозшифрований текст:\n{decrypted_text}")