from collections import Counter
import openpyxl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Шифр Віженера
def vigenere_encrypt(text, key):
    key_indices = [(ord(c) - ord('а')) for c in key]
    key_len = len(key)
    result = []
    for i, ch in enumerate(text):
        offset = (ord(ch) - ord('а') + key_indices[i % key_len]) % 32
        result.append(chr(offset + ord('а')))
    return ''.join(result)

# Індекс відповідності
def index_coincidence(txt):
    n = len(txt)
    freq = Counter(txt)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1)) if n > 1 else 0

# Збереження результатів в Excel
def save_index_table(data, filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Індекси відповідності"
    ws.append([" ", "ключ", "індекс", "різниця з оригіналом"])
    for row in data:
        ws.append(row)
    wb.save(filename)

def main():
    input_file = "text.txt"
    encrypted_file = "encrypted.txt"
    excel_file = "index.xlsx"

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read().strip()

    ic_original = index_coincidence(text)

    keys = [
        "да",
        "бог",
        "вода",
        "книги",
        "приносящее",
        "атвердинебесной",
        "земляжебылабезвиднаи"
    ]

    freqs = {
        'о': 0.108510417, 'и': 0.091808616, 'е': 0.088884769, 'а': 0.074617406, 'с': 0.05749869,
        'т': 0.05739267, 'н': 0.055495494, 'в': 0.050770748, 'л': 0.044319889, 'р': 0.043031035,
        'д': 0.035737751, 'м': 0.033091561, 'п': 0.027075382, 'к': 0.026489123, 'у': 0.02587335,
        'г': 0.022136018, 'я': 0.020417356, 'ы': 0.019166612, 'б': 0.01860041, 'з': 0.016288325,
        'ь': 0.015054487, 'х': 0.011463577, 'ч': 0.010646653, 'й': 0.009415967, 'ж': 0.00894375,
        'ш': 0.007510194, 'ю': 0.007029095, 'ц': 0.005488373, 'щ': 0.003557385, 'ф': 0.002422116,
        'э': 0.001020939,
    }

    i_theor = sum(p**2 for p in freqs.values())

    results = []
    results.append(["теор. значення", "-", i_theor, "-"])
    results.append(["відкритий текст", "-", ic_original, "-"])

    ic_values = []

    # Шифрування та розрахунок індексу для кожного ключа
    with open(encrypted_file, "w", encoding="utf-8") as out:
        for key in keys:
            encrypted = vigenere_encrypt(text, key)
            ic_enc = index_coincidence(encrypted)
            diff = abs(ic_original - ic_enc)
            results.append([" ", key, ic_enc, diff])
            ic_values.append(ic_enc)
            out.write(f"ключ: {key}\n{encrypted}\n\n")

    # Збереження результатів
    save_index_table(results, excel_file)

    #  графік
    plt.figure(figsize=(8, 5))
    plt.bar(keys, ic_values, color='skyblue')
    plt.axhline(y=i_theor, color='r', linestyle='--', label='Теоретичне значення')
    plt.axhline(y=ic_original, color='g', linestyle='--', label='Відкритий текст')
    plt.xlabel("Ключ")
    plt.ylabel("Індекс відповідності")
    plt.title("Індекси відповідності для різних ключів шифру Віженера")
    plt.legend()
    plt.xticks(rotation=45, ha='right')  # Повертає підписи під кутом 45° і вирівнює вправо
    plt.tight_layout()
    plt.savefig("diagram_vigenere.png")
    plt.close()


if __name__ == "__main__":
    main()
