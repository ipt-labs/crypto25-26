import collections
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import openpyxl

result_dir = "results"
input_file = "fox.txt"
alphabet_start = 'а'
alphabet_size = 32
i_0 = 1 / alphabet_size 

keys = {
    2: "ня",
    3: "мяу",
    4: "лиса",
    5: "отдых",
    16: "абдоминопластика"
}

def filter_text(raw_text: str) -> str:
    cleaned_text = []
    for char in raw_text.lower():
        if char == 'ё':
            char = 'е'
        if alphabet_start <= char <= 'я':
            cleaned_text.append(char)
    return "".join(cleaned_text)

def vigenere_encrypt(text: str, key: str) -> str:
    if not key:
        return text
    
    encrypted_text = []
    key_len = len(key)
    
    for i, char in enumerate(text):
        p_index = ord(char) - ord(alphabet_start)
        k_index = ord(key[i % key_len]) - ord(alphabet_start)
        
        c_index = (p_index + k_index) % alphabet_size
        
        encrypted_text.append(chr(c_index + ord(alphabet_start)))
        
    return "".join(encrypted_text)

def calculate_ic(text: str) -> float:
    n = len(text)
    if n <= 1:
        return 0.0
        
    frequencies = collections.Counter(text)
    
    numerator_sum = sum(val * (val - 1) for val in frequencies.values())
    denominator = float(n * (n - 1))
    
    return numerator_sum / denominator

def main():
    os.makedirs(result_dir, exist_ok=True)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Помилка: Вхідний файл '{input_file}' не знайдено.")
        return

    cleaned_text = filter_text(raw_text)
    
    if not cleaned_text:
        print(f"Помилка: Файл '{input_file}' порожній або не містить російських літер.")
        return
        
    print(f"Текст '{input_file}' відфільтровано. Довжина: {len(cleaned_text)} символів.")
    
    ic_results = []
    
    open_text_ic = calculate_ic(cleaned_text)
    ic_results.append({
        "Description": "Open Text",
        "KeyLength r": 0,
        "IC (I(Y))": open_text_ic
    })
    print(f"IC (I(Y)) ВТ (r=0): {open_text_ic:.5f}")

    for r, key_str in keys.items():
        encrypted_text = vigenere_encrypt(cleaned_text, key_str)
        
        out_fname = os.path.join(result_dir, f"keyfile_{r}.txt")
        with open(out_fname, 'w', encoding='utf-8') as f:
            f.write(encrypted_text)
            
        encrypted_ic = calculate_ic(encrypted_text)
        ic_results.append({
            "Description": f"Encrypted r={r}",
            "KeyLength r": r,
            "IC (I(Y))": encrypted_ic
        })
        print(f"IC (r={r}): {encrypted_ic:.5f} (збережено у {out_fname})")

    df = pd.DataFrame(ic_results)
    excel_path = os.path.join(result_dir, "IC.xlsx")
    try:
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"\nРезультати IC збережено у {excel_path}")
    except Exception as e:
        excel_path = os.path.join(result_dir, "IC.csv")
        df.to_csv(excel_path, index=False)
        print(f"Результати IC успішно збережено у {excel_path}")

    encrypted_data = df[df['KeyLength r'] > 0]
    r_values = encrypted_data['KeyLength r']
    ic_values = encrypted_data['IC (I(Y))']

    plt.figure(figsize=(10, 6))
    plt.plot(r_values, ic_values, marker='o', linestyle='-', label='Спостережуваний IC (Observed IC)')
    
    plt.axhline(y=i_0, color='r', linestyle='--', label=f'I₀ = 1/32 ≈ {i_0:.5f}')
    
    plt.axhline(y=open_text_ic, color='g', linestyle=':', label=f'IC відкритого тексту ≈ {open_text_ic:.5f}')

    plt.title('Індекси відповідності ШТ в залежності від довжини ключа (r)')
    plt.xlabel('Довжина ключа (r)')
    plt.ylabel('Індекс відповідності (I(Y))')
    
    plt.xticks(list(r_values)) 
    plt.grid(True, linestyle=':')
    plt.legend()
    
    plot_path = os.path.join(result_dir, "IC_plot.png")
    plt.savefig(plot_path)
    print(f"Діаграму IC збережено у {plot_path}")
    
if __name__ == "__main__":
    main()