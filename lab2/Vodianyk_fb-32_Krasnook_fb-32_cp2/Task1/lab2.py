import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

char_to_int = {char: i for i, char in enumerate(ALPHABET)}
int_to_char = {i: char for i, char in enumerate(ALPHABET)}


def preprocess_text(text: str) -> str:
    text = text.lower()
    regex = re.compile(f'[^%s]' % re.escape(ALPHABET))
    cleaned_text = regex.sub('', text)
    return cleaned_text


def vigenere_encrypt(plaintext: str, key: str) -> str:
    ciphertext = ""
    clean_key = preprocess_text(key)
    if not clean_key:
        raise ValueError("Ключ не містить жодного символу з алфавіту.")

    key_len = len(clean_key)

    for i, char in enumerate(plaintext):
        text_int = char_to_int[char]
        key_char = clean_key[i % key_len]
        key_int = char_to_int[key_char]

        cipher_int = (text_int + key_int) % M
        ciphertext += int_to_char[cipher_int]

    return ciphertext


def calculate_ic(text: str) -> float:
    n = len(text)
    if n < 2:
        return 0.0

    counts = Counter(text)
    numerator = sum(count * (count - 1) for count in counts.values())
    denominator = n * (n - 1)
    ic = numerator / denominator
    return ic


def calculate_avg_ic_for_r(text: str, max_r: int = 30) -> dict:
    results = {}
    for r in range(2, max_r + 1):
        block_ics = []
        for i in range(r):
            sub_text = text[i::r]
            if len(sub_text) > 1:
                block_ics.append(calculate_ic(sub_text))

        if block_ics:
            results[r] = np.mean(block_ics)
        else:
            results[r] = 0.0
    return results


def calculate_dr_statistics(text: str, max_r: int = 30) -> dict:
    results = {}
    n = len(text)
    for r in range(2, max_r + 1):
        dr_count = 0
        for i in range(n - r):
            if text[i] == text[i + r]:
                dr_count += 1
        results[r] = dr_count
    return results


def get_stats_table_string(stats_dict: dict, title: str, col1: str, col2: str) -> str:
    lines = []
    lines.append(f"\n--- {title} ---")
    lines.append(f"+{'-' * 5}+{'-' * 10}+")
    lines.append(f"| {col1:<3} | {col2:<8} |")
    lines.append(f"+{'-' * 5}+{'-' * 10}+")
    for r, val in stats_dict.items():
        if isinstance(val, float):
            lines.append(f"| {r:<3} | {val:<8.5f} |")
        else:
            lines.append(f"| {r:<3} | {val:<8} |")
    lines.append(f"+{'-' * 5}+{'-' * 10}+")
    return "\n".join(lines)


def save_plot_statistics(all_stats: dict, y_label: str, title: str, filename: str):
    num_plots = len(all_stats)
    fig, axes = plt.subplots(num_plots, 1, figsize=(10, 4 * num_plots), sharex=True)
    if num_plots == 1:
        axes = [axes]

    fig.suptitle(title, fontsize=16)

    for ax, (name, stats) in zip(axes, all_stats.items()):
        r_values = list(stats.keys())
        stat_values = list(stats.values())

        ax.plot(r_values, stat_values, marker='o', linestyle='-')
        ax.bar(r_values, stat_values, alpha=0.3)
        ax.set_title(name)
        ax.set_ylabel(y_label)
        ax.grid(True, linestyle=':')
        ax.set_xticks(r_values)

    axes[-1].set_xlabel("Довжина ключа (r)")
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])

    try:
        plt.savefig(filename)
        print(f" -> Графік збережено у файл: {filename}")
    except IOError as e:
        print(f" !! Помилка збереження графіку {filename}: {e}")

    plt.close(fig)


def main():
    keys = [
        "да",
        "дом",
        "река",
        "слово",
        "преступлениеинаказание"
    ]

    filename = r"text-lab2.txt"

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Помилка: Файл '{filename}' не знайдено.")
        return

    open_text = preprocess_text(raw_text)

    if len(open_text) < 100:
        print(f"Попередження: Довжина очищеного тексту ({len(open_text)} симв.) мала.")

    print(f"--- Аналіз тексту з файлу '{filename}' ---")
    print(f"Довжина очищеного тексту (n): {len(open_text)} символів\n")

    all_ic_r_stats = {}
    all_dr_stats = {}

    ic_open_text = calculate_ic(open_text)
    print("--- Загальний Індекс Відповідності (IC) ---")
    print(f"IC Відкритого тексту (r=1): {ic_open_text:.6f}")

    all_ic_r_stats['Відкритий текст'] = calculate_avg_ic_for_r(open_text)
    all_dr_stats['Відкритий текст'] = calculate_dr_statistics(open_text)

    print("\n--- Шифрування та Аналіз ---")

    ciphertexts = {}

    for key in keys:
        clean_key = preprocess_text(key)
        r = len(clean_key)
        print(f"\nКлюч: '{key}' (довжина r = {r})")

        ciphertext = vigenere_encrypt(open_text, key)
        ciphertexts[key] = ciphertext

        output_filename = f"ciphertext_{clean_key}.txt"
        try:
            with open(output_filename, 'w', encoding='utf-8') as f_out:
                f_out.write(ciphertext)
            print(f" -> Зашифрований текст збережено: {output_filename}")
        except IOError as e:
            print(f" !! Помилка збереження файлу {output_filename}: {e}")

        ic_ciphertext = calculate_ic(ciphertext)
        print(f"Загальний IC Шифртексту: {ic_ciphertext:.6f}")

        plot_title = f"Шифртекст (ключ='{clean_key}')"
        all_ic_r_stats[plot_title] = calculate_avg_ic_for_r(ciphertext)
        all_dr_stats[plot_title] = calculate_dr_statistics(ciphertext)

    print("\n" + "=" * 40)
    print("--- Порівняння загальних IC (Завдання 2) ---")
    print(f"IC Відкритого тексту (r=1): {ic_open_text:.6f}")

    for key, ciphertext in ciphertexts.items():
        r_clean = len(preprocess_text(key))
        ic_val = calculate_ic(ciphertext)
        print(f"IC Шифртексту (r={r_clean}, ключ='{key}'): {ic_val:.6f}")

    ic_random = 1 / M
    print(f"\nТеоретичний IC (m=33): {ic_random:.6f}")
    print("=" * 40)

    print("\n--- Збереження таблиць статистики ---")
    tables_filename = "analysis_tables.txt"

    try:
        with open(tables_filename, 'w', encoding='utf-8') as f_table:
            table_str = get_stats_table_string(all_ic_r_stats['Відкритий текст'],
                                               "Відкритий текст - IC(r)", "r", "Avg. IC")
            f_table.write(table_str + "\n\n")

            table_str = get_stats_table_string(all_dr_stats['Відкритий текст'],
                                               "Відкритий текст - D(r)", "r", "D(r)")
            f_table.write(table_str + "\n\n")

            for key in keys:
                clean_key = preprocess_text(key)
                plot_title = f"Шифртекст (ключ='{clean_key}')"

                table_str = get_stats_table_string(all_ic_r_stats[plot_title],
                                                   f"{plot_title} - IC(r)", "r", "Avg. IC")
                f_table.write(table_str + "\n\n")

                table_str = get_stats_table_string(all_dr_stats[plot_title],
                                                   f"{plot_title} - D(r)", "r", "D(r)")
                f_table.write(table_str + "\n\n")

        print(f"\n -> Усі таблиці збережено у файл: {tables_filename}")

    except IOError as e:
        print(f" !! Помилка збереження файлу таблиць {tables_filename}: {e}")

    print("\n--- Збереження діаграм у файли ---")
    save_plot_statistics(all_ic_r_stats, "Середній IC блоків",
                         "Аналіз Індексу Відповідності (IC) для різних r",
                         "ic_analysis_plots.png")

    save_plot_statistics(all_dr_stats, "Кількість збігів (D_r)",
                         "Аналіз Статистики Збігів (D_r) для різних r",
                         "dr_analysis_plots.png")

if __name__ == "__main__":
    main()
