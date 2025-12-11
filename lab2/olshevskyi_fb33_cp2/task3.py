from collections import Counter

def determine_encryption_key(encrypted_file_path, key_length):
    """
    Визначає ключ шифрування на основі частотного аналізу
    
    Аргументи:
        encrypted_file_path (str): Шлях до файлу з шифротекстом
        key_length (int): Передбачувана довжина ключа
    
    Повертає:
        str: Знайдений ключ шифрування
    """
    # Зчитуємо та підготовлюємо шифротекст
    with open(encrypted_file_path, 'r', encoding='utf-8') as file:
        # Видаляємо всі пробільні символи для чистого аналізу
        encrypted_content = ''.join(file.read().split())
    
    # Розділяємо текст на групи за позицією в ключі
    character_groups = []
    for position in range(key_length):
        # Формуємо групу символів, що шифрувалися з однаковим зсувом
        group = ''.join([encrypted_content[index] for index in 
                        range(position, len(encrypted_content), key_length)])
        character_groups.append(group)
    
    # Найпоширеніші літери російської мови (за частотою вживання)
    frequent_russian_letters = ['о', 'е', 'а']
    discovered_key = []
    
    # Аналізуємо кожну групу символів окремо
    for character_group in character_groups:
        # Знаходимо найчастішу літеру в поточній групі
        most_frequent_char = Counter(character_group).most_common(1)[0][0]
        
        optimal_shift = None
        lowest_error_score = float('inf')
        
        # Перевіряємо кожну з поширених літер як можливий оригінал
        for common_letter in frequent_russian_letters:
            # Обчислюємо зсув між найчастішою літерою та поширеною літерою
            calculated_shift = (ord(most_frequent_char) - ord(common_letter)) % 32
            potential_key_char = chr(ord('а') + calculated_shift)
            
            # Оцінюємо якість зсуву через суму абсолютних різниць
            error_score = sum(abs((ord(char) - ord(potential_key_char)) % 32) 
                            for char in character_group)
            
            # Зберігаємо найкращий зсув
            if error_score < lowest_error_score:
                lowest_error_score = error_score
                optimal_shift = calculated_shift
        
        # Визначаємо літеру ключа для поточної позиції
        key_character = chr(ord('а') + optimal_shift)
        discovered_key.append(key_character)
    
    return ''.join(discovered_key)

def decode_vigenere_cipher(encrypted_text, decryption_key):
    """
    Розшифровує текст, зашифрований шифром Віженера
    
    Аргументи:
        encrypted_text (str): Зашифрований текст
        decryption_key (str): Ключ для розшифрування
    
    Повертає:
        str: Розшифрований текст
    """
    decoded_characters = []
    key_size = len(decryption_key)
    
    for index, character in enumerate(encrypted_text):
        if character in 'абвгдежзийклмнопрстуфхцчшщъыьэюя':
            # Обчислюємо зсув для поточної позиції
            current_shift = ord(decryption_key[index % key_size]) - ord('а')
            # Застосовуємо зворотний зсув для розшифрування
            decoded_character = chr((ord(character) - ord('а') - current_shift) % 32 + ord('а'))
            decoded_characters.append(decoded_character)
        else:
            # Залишаємо не-літерні символи без змін
            decoded_characters.append(character)
    
    return ''.join(decoded_characters)

def execute_decryption_process():
    """
    Основна функція для виконання процесу розшифрування
    """
    input_file_path = 'task3.txt'
    estimated_key_length = 16
    
    # Визначаємо ключ шифрування
    discovered_key = determine_encryption_key(input_file_path, estimated_key_length)
    print(f'Виявлений ключ шифрування: {discovered_key}')
    
    # Зчитуємо оригінальний шифротекст
    with open(input_file_path, 'r', encoding='utf-8') as file:
        original_encrypted_text = ''.join(file.read().split())
    
    # Розшифровуємо текст
    decrypted_content = decode_vigenere_cipher(original_encrypted_text, discovered_key)
    
    # Зберігаємо результат розшифрування
    output_file_path = 'decrypted_result.txt'
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(decrypted_content)
    
    print(f"Процес розшифрування завершено. Результат збережено у файлі '{output_file_path}'")

# Запуск програми
if __name__ == '__main__':
    execute_decryption_process()