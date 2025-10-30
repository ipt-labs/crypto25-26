import os
import re
from collections import Counter
import matplotlib.pyplot as plt
from tabulate import tabulate

# Російський алфавіт для шифрування
RUSSIAN_ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

def prepare_text_for_analysis(input_text):
    """
    Підготовка тексту для подальшого аналізу:
    - Перетворення до нижнього регістру
    - Видалення всіх символів, крім російських літер
    - Заміна літери 'ё' на 'е' для стандартизації
    
    Аргументи:
        input_text (str): Вхідний текст для обробки
    
    Повертає:
        str: Очищений та стандартизований текст
    """
    # Видаляємо всі символи, крім російських літер
    cleaned_text = re.sub(r'[^а-яё]', '', input_text.lower())
    # Замінюємо 'ё' на 'е' для уніфікації
    standardized_text = cleaned_text.replace('ё', 'е')
    return standardized_text

def apply_vigenere_cipher(text_to_encrypt, encryption_key):
    """
    Застосовує шифр Віженера для шифрування тексту
    
    Аргументи:
        text_to_encrypt (str): Текст для шифрування
        encryption_key (str): Ключ шифрування
    
    Повертає:
        str: Зашифрований текст
    """
    encrypted_chars = []
    # Попередньо обчислюємо зсуви для кожної літери ключа
    key_offsets = [RUSSIAN_ALPHABET.index(key_char) for key_char in encryption_key]
    
    # Шифруємо кожен символ тексту
    for position, character in enumerate(text_to_encrypt):
        if character in RUSSIAN_ALPHABET:
            # Визначаємо зсув для поточної позиції
            current_offset = key_offsets[position % len(encryption_key)]
            # Знаходимо індекс зашифрованого символу
            original_index = RUSSIAN_ALPHABET.index(character)
            encrypted_index = (original_index + current_offset) % len(RUSSIAN_ALPHABET)
            encrypted_chars.append(RUSSIAN_ALPHABET[encrypted_index])
        else:
            # Залишаємо не-алфавітні символи без змін
            encrypted_chars.append(character)
    
    return ''.join(encrypted_chars)

def generate_key_for_length(desired_length):
    """
    Генерує приклад ключа заданої довжини
    
    Аргументи:
        desired_length (int): Бажана довжина ключа
    
    Повертає:
        str: Ключ заданої довжини або порожній рядок, якщо ключ не знайдено
    """
    # Словник прикладів ключів різної довжини
    key_gen = {
        2: 'су',
        3: 'уьж',
        4: 'йьзс',
        5: 'ёсвмч',
        6: 'нывцкж',
        7: 'шжжтбай',
        8: 'пскврммы',
        9: 'яжелйукву',
        10: 'зтёкътвони',
        11: 'уозянгбимвз',
        12: 'яжгёгъгкялщь',
        13: 'нжввэфзкзёющс',
        14: 'ибсзюкгфшжщхаг',
        15: 'этэфазээиъъшебк',
        16: 'фмояйрщщмтыоъялх',
        17: 'йдзюмоовъгкцббхцу',
        18: 'ййкмэнтшьъфтэрвесь',
        19: 'жвупкрттаьъццмьслэт',
        20: 'ошдеьмъищчтрьшбкббах',
    }
    return key_gen.get(desired_length, '')

def create_directory_if_missing(directory_path):
    """
    Створює директорію, якщо вона не існує
    
    Аргументи:
        directory_path (str): Шлях до директорії
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def compute_index_of_coincidence(text_sample):
    """
    Обчислює індекс відповідності (Index of Coincidence) для тексту
    
    Індекс відповідності - це міра ймовірності того, що два випадкові 
    символи з тексту будуть однаковими. Використовується для криптоаналізу.
    
    Аргументи:
        text_sample (str): Текст для аналізу
    
    Повертає:
        float: Значення індексу відповідності
    """
    processed_text = prepare_text_for_analysis(text_sample)
    text_length = len(processed_text)
    
    # Якщо текст занадто короткий, повертаємо 0
    if text_length <= 1:
        return 0.0
    
    # Підраховуємо частоти кожної літери
    character_frequencies = Counter(processed_text)
    
    # Обчислюємо індекс відповідності за формулою:
    # IC = Σ(f_i * (f_i - 1)) / (n * (n - 1))
    # де f_i - частота i-ї літери, n - довжина тексту
    coincidence_sum = sum(freq * (freq - 1) for freq in character_frequencies.values())
    index_of_coincidence = coincidence_sum / (text_length * (text_length - 1))
    
    return index_of_coincidence

# Головна функція програми
if __name__ == "__main__":
    # Зчитування та підготовка вихідного тексту
    with open('task1.txt', 'r', encoding='utf-8') as input_file:
        source_text = prepare_text_for_analysis(input_file.read())

    # Налаштування шляху для збереження результатів
    output_directory = 'encryption_results'
    create_directory_if_missing(output_directory)

    print("Початок процесу шифрування...")
    
    # Шифрування тексту з ключами різної довжини
    for key_size in range(2, 20):
        cipher_key = generate_key_for_length(key_size)
        encrypted_text = apply_vigenere_cipher(source_text, cipher_key)
        
        # Збереження зашифрованого тексту у файл
        output_file_path = os.path.join(output_directory, f'encrypted_key_length_{key_size}.txt')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(encrypted_text)

    print(f"Шифрування завершено. Результати збережено в директорії '{output_directory}'.")

    # Аналіз індексів відповідності для зашифрованих текстів
    print("\nОбчислення індексів відповідності...")
    analysis_results = []
    
    for key_size in range(2, 21):
        file_path = os.path.join(output_directory, f'encrypted_key_length_{key_size}.txt')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as encrypted_file:
                cipher_text = encrypted_file.read()
                ic_value = compute_index_of_coincidence(cipher_text)
                analysis_results.append((key_size, ic_value))

    # Вивід результатів у вигляді таблиці
    table_headers = ["Довжина ключа", "Індекс відповідності"]
    formatted_table = [[length, f"{ic:.10f}"] for length, ic in analysis_results]
    print("\nРезультати аналізу індексів відповідності:")
    print(tabulate([table_headers] + formatted_table, headers="firstrow", tablefmt="grid"))

    # Візуалізація результатів
    key_lengths, ic_values = zip(*analysis_results)
    
    plt.figure(figsize=(12, 7))
    # Графік залежності індексу відповідності від довжини ключа
    plt.plot(key_lengths, ic_values, marker='o', linewidth=2, markersize=8, 
             label='Індекс відповідності зашифрованого тексту')
    
    # Горизонтальна лінія для порівняння з IC відкритого тексту
    plt.axhline(y=0.055, color='red', linestyle='--', linewidth=2, 
                label='IC типового відкритого тексту (0.055)')
    
    plt.title('Залежність індексу відповідності від довжини ключа шифру', fontsize=14, pad=20)
    plt.xlabel('Довжина ключа шифру', fontsize=12)
    plt.ylabel('Індекс відповідності', fontsize=12)
    plt.xticks(key_lengths)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()