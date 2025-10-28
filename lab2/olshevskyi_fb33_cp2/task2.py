import matplotlib.pyplot as plt
from collections import Counter

# Російський алфавіт для аналізу
RUSSIAN_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

def read_and_prepare_text(input_file_path):
    """
    Зчитує та підготовлює текст для частотного аналізу
    
    Аргументи:
        input_file_path (str): Шлях до файлу з текстом
    
    Повертає:
        str: Підготовлений текст у верхньому регістрі
    """
    with open(input_file_path, 'r', encoding='utf-8') as file:
        original_text = file.read()
        # Стандартизуємо текст: заміна ё на е, видалення переносів, верхній регістр
        processed_text = (original_text.replace('ё', 'е')
                         .replace('\n', '')
                         .upper())
    return processed_text

def calculate_coincidence_index(text_sample):
    """
    Обчислює індекс відповідності (Index of Coincidence) для тексту
    
    Індекс відповідності показує ймовірність того, що два випадкові 
    символи з тексту збігаються. Використовується для оцінки 
    рівномірності розподілу символів.
    
    Аргументи:
        text_sample (str): Текст для аналізу
    
    Повертає:
        float: Значення індексу відповідності
    """
    text_length = len(text_sample)
    # Для коротких текстів індекс не має сенсу
    if text_length < 2:
        return 0.0
    
    # Підрахунок частоти кожного символу
    character_frequencies = Counter(text_sample)
    
    # Формула індексу відповідності: 
    # IC = Σ(f_i * (f_i - 1)) / (n * (n - 1))
    # де f_i - частота i-го символу, n - довжина тексту
    numerator = sum(freq * (freq - 1) for freq in character_frequencies.values())
    denominator = text_length * (text_length - 1)
    coincidence_index = numerator / denominator
    
    return coincidence_index

def split_text_into_blocks(original_text, block_size):
    """
    Розбиває текст на блоки для аналізу різних позицій ключа
    
    Аргументи:
        original_text (str): Вихідний текст
        block_size (int): Розмір блоку (довжина ключа)
    
    Повертає:
        list: Список блоків, де кожен блок містить символи, 
              що шифрувалися з однаковим зсувом
    """
    blocks = []
    for start_position in range(block_size):
        # Формуємо блок символів, що йдуть через інтервал block_size
        block = ''.join(original_text[position] for position in 
                       range(start_position, len(original_text), block_size))
        blocks.append(block)
    return blocks

def compute_average_ic_for_key_lengths(text_to_analyze, maximum_key_length):
    """
    Обчислює середній індекс відповідності для різних довжин ключа
    
    Аргументи:
        text_to_analyze (str): Текст для аналізу
        maximum_key_length (int): Максимальна довжина ключа для перевірки
    
    Повертає:
        list: Список кортежів (довжина_ключа, середній_IC)
    """
    results = []
    
    for current_key_length in range(2, maximum_key_length + 1):
        # Розбиваємо текст на блоки для поточної довжини ключа
        text_blocks = split_text_into_blocks(text_to_analyze, current_key_length)
        
        # Обчислюємо IC для кожного блоку
        block_ic_values = [calculate_coincidence_index(block) for block in text_blocks]
        
        # Розраховуємо середнє значення IC для всіх блоків
        average_ic = sum(block_ic_values) / len(block_ic_values)
        results.append((current_key_length, average_ic))
    
    return results

def plot_ic_analysis_results(ic_analysis_data):
    """
    Створює графік залежності індексу відповідності від довжини ключа
    
    Аргументи:
        ic_analysis_data (list): Дані для візуалізації у форматі 
                                [(довжина, IC), ...]
    """
    key_lengths, ic_values = zip(*ic_analysis_data)
    
    plt.figure(figsize=(12, 7))
    plt.plot(key_lengths, ic_values, marker='o', linewidth=2, markersize=6, 
             label='Середній індекс відповідності')
    
    # Додаємо горизонтальну лінію для орієнтиру (типовий IC російського тексту)
    plt.axhline(y=0.055, color='red', linestyle='--', alpha=0.7,
                label='Очікуваний IC для російського тексту (~0.055)')
    
    plt.title('Аналіз індексу відповідності для визначення довжини ключа', 
              fontsize=14, pad=20)
    plt.xlabel('Довжина ключа', fontsize=12)
    plt.ylabel('Індекс відповідності', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.xticks(range(2, len(key_lengths) + 2))
    plt.tight_layout()
    plt.show()

def perform_ic_analysis():
    """
    Основна функція для виконання аналізу індексу відповідності
    """
    # Шлях до файлу з шифротекстом
    input_file_path = 'task3.txt'
    
    # Максимальна довжина ключа для аналізу
    max_key_length_to_test = 30
    
    # Завантаження та підготовка тексту
    print("Завантаження та підготовка тексту...")
    encrypted_text = read_and_prepare_text(input_file_path)
    print(f"Розмір тексту: {len(encrypted_text)} символів")
    
    # Обчислення індексів відповідності
    print("Обчислення індексів відповідності для різних довжин ключа...")
    ic_analysis_results = compute_average_ic_for_key_lengths(
        encrypted_text, max_key_length_to_test
    )
    
    # Вивід результатів
    print("\nРезультати аналізу:")
    print("Довжина ключа | Індекс відповідності")
    print("-" * 40)
    for key_len, ic_val in ic_analysis_results:
        print(f"{key_len:13} | {ic_val:.6f}")
    
    # Візуалізація результатів
    print("\nПобудова графіка...")
    plot_ic_analysis_results(ic_analysis_results)
    
    # Пошук найбільш ймовірної довжини ключа
    most_likely_length = max(ic_analysis_results, key=lambda x: x[1])[0]
    print(f"\nНайбільш ймовірна довжина ключа: {most_likely_length}")

# Запуск програми
if __name__ == "__main__":
    perform_ic_analysis()