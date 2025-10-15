#!/usr/bin/env python3
import csv
import math
from pathlib import Path
from collections import Counter
import re
from typing import Dict, Any
import matplotlib.pyplot as plt

INPUT_FILE = Path("lab2.txt")
OUT_DIR = Path("out")
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = 32

MI_RUSSIAN = 0.0574
I0_UNIFORM = 1 / M


def read_text(p: Path) -> str:
    return p.read_bytes().decode("utf-8", "ignore")

def char_to_num(char: str) -> int:
    return ALPHABET.index(char)

def num_to_char(num: int) -> str:
    return ALPHABET[num]

def prepare_text(text: str) -> str:
    s = text.lower()
    s = s.replace('ё', 'е')
    allowed_chars = set(ALPHABET)
    s = "".join(c for c in s if c in allowed_chars)
    return s

def vigenere_encrypt(plaintext: str, key: str) -> str:
    key = prepare_text(key)
    if not key:
        raise ValueError("Ключ не може бути порожнім.")
        
    encrypted_text = []
    key_len = len(key)
    
    for i, char_x in enumerate(plaintext):
        x = char_to_num(char_x)
        k = char_to_num(key[i % key_len])
        
        y = (x + k) % M
        encrypted_text.append(num_to_char(y))
        
    return "".join(encrypted_text)

def index_of_coincidence(text: str) -> float:
    n = len(text)
    if n < 2:
        return 0.0

    counts = Counter(text)
    sum_nt_nt_minus_1 = 0
    
    for t in ALPHABET:
        Nt = counts.get(t, 0)
        sum_nt_nt_minus_1 += Nt * (Nt - 1)
        
    return sum_nt_nt_minus_1 / (n * (n - 1))

def save_summary(path: Path, summaries: list[Dict[str, Any]]):
    if not summaries:
        return

    keys = list(summaries[0].keys())
    
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(summaries)

def plot_ic_vs_r(results: list[Dict[str, Any]], out_dir: Path):
    ciphertext_results = [
        {'r': res['r_len'], 'IC': float(res['IC'])}
        for res in results if res['r_len'] > 1
    ]
    
    r_values = [res['r'] for res in ciphertext_results]
    ic_values = [res['IC'] for res in ciphertext_results]

    plt.figure(figsize=(10, 6))
    
    plt.plot(r_values, ic_values, marker='o', linestyle='-', color='b', label='Observed IC')
    
    plt.axhline(y=I0_UNIFORM, color='r', linestyle='--', label=f'$I_0 = 1/m \\approx {I0_UNIFORM:.5f}$')
    
    plt.title('Індекси відповідності шифртексту в залежності від довжини ключа (r)', fontsize=14)
    plt.xlabel('Довжина ключа (r)', fontsize=12)
    plt.ylabel('Індекс відповідності I(Y)', fontsize=12)
    
    plt.ylim(0.03, 0.06) 
    
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    plt.xticks(r_values)
    
    plot_path = out_dir / "ic_vs_r_plot.png"
    plt.savefig(plot_path)
    plt.close()


def main():
    
    raw_text_from_file = read_text(INPUT_FILE)
    plaintext = prepare_text(raw_text_from_file)
    n_chars = len(plaintext)
    
    keys_to_test = {
        'да': 2,
        'три': 3,
        'шифр': 4,
        'слово': 5,
        'криптоанализ': 12 
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    results = []
    pt_file = OUT_DIR / "plaintext.txt"
    pt_file.write_text(plaintext, encoding='utf-8')
    ic_pt = index_of_coincidence(plaintext)
    
    results.append({
        'Text_Type': 'PT',
        'Key': 'N/A',
        'r_len': 1,
        'IC': f"{ic_pt:.10f}",
        'Expected_IC': f"{MI_RUSSIAN:.5f}"
    })

    for key, r in keys_to_test.items():
        ciphertext = vigenere_encrypt(plaintext, key)
        ic_ct = index_of_coincidence(ciphertext)
        
        ct_filename = f"file_key{r}.txt"
        ct_file = OUT_DIR / ct_filename
        ct_file.write_text(ciphertext, encoding='utf-8')

        results.append({
            'Text_Type': 'CT',
            'Key': key.upper(),
            'r_len': r,
            'IC': f"{ic_ct:.10f}",
            'Expected_IC': f"{I0_UNIFORM:.5f}"
        })
        
    save_summary(OUT_DIR / "ic_summary.csv", results)
    plot_ic_vs_r(results, OUT_DIR)

    print(f"\n--- ЗВЕДЕНА ТАБЛИЦЯ ІНДЕКСІВ ВІДПОВІДНОСТІ (Завдання 2) ---")
    print(f"| {'Тип':<10} | {'r':<2} | {'Ключ':<13} | {'Обчислений IC':<15} | {'Очікуваний IC':<13} |")
    print("-" * 69)
    
    for res in results:
        print(f"| {res['Text_Type']:<10} | {res['r_len']:<2} | {res['Key']:<13} | {res['IC']:<15} | {res['Expected_IC']:<13} |")
        
    print("-" * 69)
    print(f"Усі файли (включно з ic_summary.csv та ic_vs_r_plot.png) збережено в каталозі: {OUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
