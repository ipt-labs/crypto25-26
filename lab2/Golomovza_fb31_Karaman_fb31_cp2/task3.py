import matplotlib.pyplot as plt
from collections import Counter

# Російський алфавіт
RUS_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# Функція для читання тексту з файлу
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read().replace('ё', 'е').replace('\n', '').upper()
    return text

# Функція для обчислення індексу відповідності
def compute_ic(text):
    n = len(text)
    if n < 2:
        return 0
    freq = Counter(text)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

# Розбиття тексту на блоки
def divide_into_blocks(text, block_size):
    return [''.join(text[i::block_size]) for i in range(block_size)]

# Середній індекс відповідності для заданої довжини ключа
def calculate_avg_ic(text, max_length):
    results = []
    for length in range(2, max_length + 1):
        blocks = divide_into_blocks(text, length)
        ic_values = [compute_ic(block) for block in blocks]
        avg_ic = sum(ic_values) / len(ic_values)
        results.append((length, avg_ic))
    return results

# Побудова графіка
def visualize_ic(ic_data):
    lengths, values = zip(*ic_data)
    plt.figure(figsize=(10, 6))
    plt.plot(lengths, values, marker='o', label='IC для довжин ключа')
    plt.title('Залежність індексу відповідності від довжини ключа')
    plt.xlabel('Довжина ключа')
    plt.ylabel('Індекс відповідності')
    plt.grid(True)
    plt.legend()
    plt.show()

# Основний блок
if __name__ == "__main__":
    # Шлях до файлу
    file_path = 'text.txt'

    # Завантаження шифртексту
    cipher_text = load_text(file_path)

    # Максимальна довжина ключа
    max_key_length = 30

    # Розрахунок середнього індексу відповідності
    ic_results = calculate_avg_ic(cipher_text, max_key_length)

    # Візуалізація
    visualize_ic(ic_results)