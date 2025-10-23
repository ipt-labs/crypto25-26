from collections import Counter
import openpyxl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def vigenere_encrypt(plain_text, encryption_key):
    key_indices = [(ord(char) - ord('а')) for char in encryption_key]
    key_length = len(encryption_key)
    encrypted_chars = []
    
    for i, char in enumerate(plain_text):
        if 'а' <= char <= 'я':
            offset = (ord(char) - ord('а') + key_indices[i % key_length]) % 32
            encrypted_chars.append(chr(offset + ord('а')))
        else:
            encrypted_chars.append(char)
            
    return ''.join(encrypted_chars)

def calculate_index_of_coincidence(text_input):
    filtered_text = ''.join(filter(lambda char: 'а' <= char <= 'я', text_input.lower()))
    text_length = len(filtered_text)
    
    if text_length <= 1:
        return 0
        
    char_frequencies = Counter(filtered_text)
    
    numerator = sum(freq * (freq - 1) for freq in char_frequencies.values())
    denominator = text_length * (text_length - 1)
    
    return numerator / denominator

def save_results_to_excel(results_data, output_filename):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Індекси відповідності"
    
    worksheet.append(["Тип тексту", "Ключ", "Індекс відповідності", "Різниця з оригіналом"])
    
    for row_data in results_data:
        worksheet.append(row_data)
        
    workbook.save(output_filename)

def create_plot(ic_values, original_ic, theoretical_ic, x_axis_labels, output_filename):
    x_positions = range(len(x_axis_labels))

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 7))

    plt.bar(x_positions, ic_values, color='purple', label='Індекс шифротексту')

    plt.axhline(y=theoretical_ic, color='crimson', linestyle='--', label=f'Теоретичне значення ({theoretical_ic:.4f})')
    plt.axhline(y=original_ic, color='limegreen', linestyle='--', label=f'Індекс відкритого тексту ({original_ic:.4f})')

    plt.xlabel("Довжина ключа", fontsize=12)
    plt.ylabel("Індекс відповідності", fontsize=12)
    plt.title("Індекс відповідності для ключів різної довжини шифру Віженера", fontsize=16, pad=20)
    plt.legend(fontsize=10)
    
    plt.xticks(x_positions, x_axis_labels)
    plt.grid(True, axis='y', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    plt.savefig(output_filename)
    plt.close()

def main():
    input_filename = input("Введіть назву файлу для шифрування (наприклад, text.txt): ")
    encrypted_filename = "encrypted_text.txt"
    excel_filename = "coincidence_indices.xlsx"
    plot_filename = "vigenere_plot.png"

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            raw_text = f.read().lower().replace('ё', 'е').strip()
            plain_text = ''.join(char for char in raw_text if 'а' <= char <= 'я' or char == ' ')
    except FileNotFoundError:
        print(f"Помилка: Файл '{input_filename}' не знайдено.")
        return

    original_ic = calculate_index_of_coincidence(plain_text)

    encryption_keys = [
        "ад", "фхц", "йшзщ", "пнмгв", "юэьыъщшчцф", "йгяфпнвмзщд",
        "цбшйгчхэзщдв", "хцбшйгчэзщдвм", "пгцъуачзйвмшхю", "пртлгшщзжюбьмхц",
        "щдвмхчюъягбшйпцз", "гцъуачзйвмшхюьфнп", "чшнмзщдгуяпфхцбйвэ", "фбьмюжзщшгнекпрсмтв", "бюлйувшгячхэзщдфнмцп"
    ]

    char_frequencies = {
        'о': 0.1037871035, 'и': 0.0867394604, 'е':0.0878555126, 'а': 0.0829055014, 'с': 0.0495496985,
        'т': 0.0635783234, 'н': 0.0643695491, 'в': 0.0479794641, 'л': 0.0488842353, 'р': 0.0412393138,
        'д': 0.0314535556, 'м': 0.0337172802, 'п': 0.0256325493, 'к': 0.0261693755, 'у': 0.0282879343,
        'г': 0.0169161315, 'я': 0.0198431634, 'ы': 0.0207939278, 'б': 0.0174852966, 'з': 0.0168952909,
        'ь': 0.0148809353, 'х': 0.0163670885, 'ч': 0.0103462996, 'й': 0.0096944906, 'ж': 0.0098928360,
        'ш': 0.0067753638, 'ю': 0.0072935052, 'ц': 0.0020114810, 'щ': 0.0054674340, 'ф': 0.0004405280,
        'э': 0.0027473712
    }

    theoretical_ic = sum(p**2 for p in char_frequencies.values())

    analysis_results = [
        ["Теоретичне значення", "-", f"{theoretical_ic:.6f}", "-"],
        ["Відкритий текст", "-", f"{original_ic:.6f}", "-"]
    ]
    
    encrypted_ic_values = []

    with open(encrypted_filename, "w", encoding="utf-8") as output_file:
        for current_key in encryption_keys:
            encrypted_text = vigenere_encrypt(plain_text, current_key)
            encrypted_ic = calculate_index_of_coincidence(encrypted_text)
            ic_difference = abs(original_ic - encrypted_ic)
            
            analysis_results.append([f"Шифротекст (ключ: {len(current_key)})", current_key, f"{encrypted_ic:.6f}", f"{ic_difference:.6f}"])
            encrypted_ic_values.append(encrypted_ic)
            
            output_file.write(f"Ключ: {current_key} (довжина: {len(current_key)})\n")
            output_file.write(f"{encrypted_text}\n\n")

    save_results_to_excel(analysis_results, excel_filename)
    print(f"Таблиця з індексами збережена у файл: {excel_filename}")
    
    key_lengths = [len(k) for k in encryption_keys]
    min_len = min(key_lengths)
    max_len = max(key_lengths)

    ic_map = dict(zip(key_lengths, encrypted_ic_values))

    plot_x_axis_labels = list(range(min_len, max_len + 1))
    plot_ic_values = [ic_map.get(length, 0) for length in plot_x_axis_labels]
    
    create_plot(plot_ic_values, original_ic, theoretical_ic, plot_x_axis_labels, plot_filename)
    print(f"Діаграма збережена у файл: {plot_filename}")

if __name__ == "__main__":
    main()

