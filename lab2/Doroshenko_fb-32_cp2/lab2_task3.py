import collections
import matplotlib.pyplot as plt


ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
N = len(ALPHABET)
RUS_FREQS = {
    'а': 0.0799, 'б': 0.0159, 'в': 0.0448, 'г': 0.0170, 'д': 0.0298, 'е': 0.0849,
    'ж': 0.0094, 'з': 0.0165, 'и': 0.0735, 'й': 0.0121, 'к': 0.0349, 'л': 0.0440,
    'м': 0.0321, 'н': 0.0670, 'о': 0.1097, 'п': 0.0281, 'р': 0.0473, 'с': 0.0547,
    'т': 0.0626, 'у': 0.0262, 'ф': 0.0026, 'х': 0.0097, 'ц': 0.0048, 'ч': 0.0144,
    'ш': 0.0073, 'щ': 0.0036, 'ъ': 0.0004, 'ы': 0.0190, 'ь': 0.0174, 'э': 0.0032,
    'ю': 0.0064, 'я': 0.0201
}

# Розрахунок індексу відповідності
def get_ic(text):
    if len(text) <= 1: return 0
    counts = collections.Counter(text)
    length = len(text)
    return sum(f * (f - 1) for f in counts.values()) / (length * (length - 1))

# Знаходження найбільш ймовірної довжини ключа r
def find_key_length(ciphertext, max_r=30):
    r_values = []
    dr_values = []
    best_r = 0
    max_ic = 0

    print(f"{'r':<5} | {'Середній індекс (Dr)':<20}")
    for r in range(2, max_r + 1):
        avg_ic = sum(get_ic(ciphertext[i::r]) for i in range(r)) / r
        r_values.append(r)
        dr_values.append(avg_ic)
        print(f"{r:<5} | {avg_ic:.5f}")

        if avg_ic > max_ic:
            max_ic = avg_ic
            best_r = r

    return best_r, r_values, dr_values

# Визначення символів ключа на основі частотного аналізу
def find_key(ciphertext, r):
    key = ""
    for i in range(r):
        group = ciphertext[i::r]
        best_shift = 0
        min_chi_sq = float('inf')

        for shift in range(N):
            chi_sq = 0
            for char_idx in range(N):
                char = ALPHABET[(char_idx + shift) % N]
                observed = group.count(char) / len(group)
                expected = RUS_FREQS.get(ALPHABET[char_idx], 0)
                chi_sq += ((observed - expected)**2) / (expected if expected > 0 else 1)

            if chi_sq < min_chi_sq:
                min_chi_sq = chi_sq
                best_shift = shift
        key += ALPHABET[best_shift]
    return key

# Розшифровка тексту шифром Віженера
def decrypt_vigenere(ciphertext, key):
    plaintext = ""
    for i, char in enumerate(ciphertext):
        char_idx = ALPHABET.index(char)
        key_idx = ALPHABET.index(key[i % len(key)])
        plaintext += ALPHABET[(char_idx - key_idx) % N]
    return plaintext

# Побудова та зберігання діаграми індексів відповідності
def plot_dr(r_values, dr_values, best_r, save_path):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(r_values, dr_values, color='skyblue', edgecolor='navy')
    bars[best_r - 2].set_color('orange')
    bars[best_r - 2].set_edgecolor('red')

    plt.axhline(y=0.0553, color='red', linestyle='--', alpha=0.6, label='Індекс мови (~0.0553)')
    plt.title(f'Аналіз Dr (Виявлено період r={best_r})', fontsize=14)
    plt.xlabel('Довжина ключа (r)')
    plt.ylabel('Середній індекс (Dr)')
    plt.xticks(r_values)
    plt.legend()
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    plt.savefig(save_path)

def main():
    # Шляхи до файлів
    input_file = "lab2/Doroshenko_fb-32_cp2/text_var6.txt"
    output_file = "lab2/Doroshenko_fb-32_cp2/decrypted_text_var6.txt"
    chart_file = "lab2/Doroshenko_fb-32_cp2/task3_dr_chart.png"

    # Завантаження та підготовка тексту
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            ciphertext = "".join([c for c in content if c in ALPHABET])
    except FileNotFoundError:
        print(f"Помилка: Файл {input_file} не знайдено.")
        return

    # Розрахунок Dr та пошук періоду
    best_r, r_list, dr_list = find_key_length(ciphertext)

    # Візуалізація
    plot_dr(r_list, dr_list, best_r, chart_file)
    print(f"\nДіаграму збережено: {chart_file}")

    # Пошук ключа
    key = find_key(ciphertext, best_r)
    print(f"Знайдений ключ: {key}")

    # Дешифрування та збереження
    plaintext = decrypt_vigenere(ciphertext, key)
    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(plaintext)

    print(f"Результат збережено: {output_file}")

if __name__ == "__main__":
    main()
