import matplotlib.pyplot as plt
import numpy as np


def calculate_coincidences(text, max_len=30):

    cleaned_text = ''.join(filter(str.isalpha, text)).upper()

    n = len(cleaned_text)
    key_lengths = list(range(2, max_len + 1))
    coincidences = []

    for r in key_lengths:
        count = 0
        for i in range(n - r):
            if cleaned_text[i] == cleaned_text[i + r]:
                count += 1
        coincidences.append(count)

    return key_lengths, coincidences


file_name = 'var_3.txt'

try:
    with open(file_name, 'r', encoding='utf-8') as f:
        ciphertext = f.read()
except FileNotFoundError:
    print(f"ПОМИЛКА: Файл '{file_name}' не знайдено")

    exit()

max_key_length = 30
key_lengths, coincidences = calculate_coincidences(ciphertext, max_key_length)

plt.figure(figsize=(14, 7))
bars = plt.bar(key_lengths, coincidences, color='grey',
               label='Кількість збігів (D_r)')

plt.title('Аналіз довжини ключа', fontsize=16)
plt.xlabel('Можлива довжина ключа', fontsize=12)
plt.ylabel('Кількість збігів', fontsize=12)

plt.xticks(np.arange(min(key_lengths), max(key_lengths) + 1, 1.0))

plt.grid(axis='y', linestyle='--', alpha=0.7)

try:
    index_14 = key_lengths.index(14)
    bars[index_14].set_color('red')
except ValueError:
    print("Попередження: довжина ключа 14 не аналізувалася.")

try:
    index_28 = key_lengths.index(28)
    bars[index_28].set_color('red')

    max_val = coincidences[index_28]
    max_r = key_lengths[index_28]

    plt.text(max_r, max_val + 5,  # Позиція тексту (трохи вище стовпця)
             f'Найвищий пік: r={max_r} ({max_val})',
             horizontalalignment='center',
             color='blue',
             fontweight='bold')

except ValueError:
    print("Попередження: довжина ключа 28 не аналізувалася.")

plt.legend()
plt.show()
