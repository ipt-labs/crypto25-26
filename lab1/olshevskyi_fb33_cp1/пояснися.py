import math

# Визначаємо російський алфавіт у нижньому регістрі
RUS_ALPHA_LOWER = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
# Генеруємо верхній регістр на основі нижнього
RUS_ALPHA_UPPER = RUS_ALPHA_LOWER.upper()

# Функція для очищення тексту: залишає лише літери російського алфавіту і пробіли (за потребою)
def filter_russian_text(txt, allow_spaces=True):
    # Видаляємо зайві пробіли між словами
    txt = ' '.join(txt.split())
    # Залишаємо тільки допустимі символи
    txt = ''.join(
        ch for ch in txt
        if ch in RUS_ALPHA_LOWER or ch in RUS_ALPHA_UPPER or (allow_spaces and ch == ' ')
    )
    # Перетворюємо все на нижній регістр для уніфікації
    return txt.lower()

# Функція підрахунку кількості кожного символу у тексті
def count_chars(txt):
    counts = {}
    for ch in txt:
        counts[ch] = counts.get(ch, 0) + 1
    return counts

# Функція підрахунку біграм (послідовностей з двох символів)
def count_bigrams(txt):
    counts = {}
    for i in range(len(txt) - 1):
        pair = txt[i:i+2]
        counts[pair] = counts.get(pair, 0) + 1
    return counts

# Обчислення ентропії на основі частот символів чи біграм
def calculate_entropy(txt, freq_dict):
    entropy = 0.0
    length = len(txt)
    for count in freq_dict.values():
        p = count / length  # Ймовірність символу
        entropy += p * math.log2(p)  # Внесок у ентропію
    return -entropy  # Ентропія визначається як -Σp*log2(p)

# Функція для обчислення надлишковості тексту
def redundancy(entropy_val, alphabet_sz):
    # Надлишковість = 1 - (H / log2(розмір алфавіту))
    return 1 - (entropy_val / math.log2(alphabet_sz))

# Функція збереження частот у файл
def save_freq(freq_dict, txt, file_obj, heading="Частоти символів"):
    file_obj.write(f"\n=== {heading} ===\n")
    file_obj.write(f"{'Символ':<5} {'Кількість':<10} {'% від загального':<15}\n")
    length = len(txt)
    # Сортуємо за частотою від більшого до меншого
    for k, v in sorted(freq_dict.items(), key=lambda x: x[1], reverse=True):
        file_obj.write(f"{k:<5} {v:<10} {v/length*100:>10.3f}%\n")

# Зчитування тексту з файлу
file_path = r'C:\Users\Apollon\Desktop\3year\stuff\crypto\lab 1\TEXT.txt'
with open(file_path, 'r', encoding='utf-8') as f:
    raw_text = f.read()

# Очищення тексту з пробілами та без пробілів
text_with_spaces = filter_russian_text(raw_text, allow_spaces=True)
text_without_spaces = filter_russian_text(raw_text, allow_spaces=False)

# Збереження очищеного тексту у окремі файли
with open('output_with_spaces.txt', 'w', encoding='utf-8') as f:
    f.write(text_with_spaces)
with open('output_without_spaces.txt', 'w', encoding='utf-8') as f:
    f.write(text_without_spaces)

# Підрахунок частот символів та біграм
freq_with_spaces = count_chars(text_with_spaces)
freq_without_spaces = count_chars(text_without_spaces)
bigrams_with_spaces = count_bigrams(text_with_spaces)
bigrams_without_spaces = count_bigrams(text_without_spaces)

# Обчислення ентропії для символів та біграм
entropy_with_spaces = calculate_entropy(text_with_spaces, freq_with_spaces)
entropy_without_spaces = calculate_entropy(text_without_spaces, freq_without_spaces)
entropy_bigrams_with_spaces = calculate_entropy(text_with_spaces, bigrams_with_spaces)
entropy_bigrams_without_spaces = calculate_entropy(text_without_spaces, bigrams_without_spaces)

# Збереження результатів аналізу у файл
with open('analysis_results.txt', 'w', encoding='utf-8') as f:
    save_freq(freq_with_spaces, text_with_spaces, f, "Літери з пробілами ")
    save_freq(freq_without_spaces, text_without_spaces, f, "Літери без пробілів ")
    save_freq(bigrams_with_spaces, text_with_spaces, f, "Біграми з пробілами ")
    save_freq(bigrams_without_spaces, text_without_spaces, f, "Біграми без пробілів ")

    # Записуємо ентропії у файл
    f.write(f"\nЕнтропія літер з пробілами: {entropy_with_spaces:.4f}\n")
    f.write(f"Ентропія літер без пробілів: {entropy_without_spaces:.4f}\n")
    f.write(f"Ентропія біграм з пробілами: {entropy_bigrams_with_spaces:.4f}\n")
    f.write(f"Ентропія біграм без пробілів: {entropy_bigrams_without_spaces:.4f}\n")

    # Записуємо надлишковість
    f.write(f"\nНадлишковість літер з пробілами: {redundancy(entropy_with_spaces, 34):.4f}\n")
    f.write(f"Надлишковість літер без пробілів: {redundancy(entropy_without_spaces, 33):.4f}\n")
    f.write(f"Надлишковість біграм з пробілами: {redundancy(entropy_bigrams_with_spaces, 34**2):.4f}\n")
    f.write(f"Надлишковість біграм без пробілів: {redundancy(entropy_bigrams_without_spaces, 33**2):.4f}\n")
