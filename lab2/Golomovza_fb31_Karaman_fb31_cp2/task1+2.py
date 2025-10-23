import os
import re
from collections import Counter
import matplotlib.pyplot as plt
import sys
sys.stdout.reconfigure(encoding='utf-8')

ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

def clean_text(txt):
    return re.sub(r'[^а-яё]', '', txt.lower()).replace('ё', 'е')

def vigenere_encrypt(txt, key):
    res = []
    key_shift = [ALPHABET.index(k) for k in key]
    for i, ch in enumerate(txt):
        if ch in ALPHABET:
            shift = key_shift[i % len(key)]
            res.append(ALPHABET[(ALPHABET.index(ch) + shift) % len(ALPHABET)])
    return ''.join(res)

def index_of_coincidence(txt):
    txt = clean_text(txt)
    n = len(txt)
    if n <= 1:
        return 0
    freq = Counter(txt)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

def get_key(length):
    s = {
        2: 'он', 3: 'лет', 4: 'сила', 5: 'время',
        6: 'знание', 7: 'техника', 8: 'история', 9: 'универсал',
        10: 'природный', 11: 'исследование', 12: 'математически',
        13: 'прикладнаянаука', 14: 'фундаментальная',
        15: 'развитиеобщества', 16: 'взаимодействиеидей',
        17: 'современныепроцессы', 18: 'прогрессивныетехнологии',
        19: 'разнообразныенаправления', 20: 'влияниецивилизации'
    }
    return s.get(length, 'ключ')

def make_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)

if __name__ == "__main__":
    with open('text1.txt', 'r', encoding='utf-8') as f:
        text = clean_text(f.read())

    out_dir = 'encrypt'
    make_dir(out_dir)

    results = []
    for key_len in range(2, 21):
        key = get_key(key_len)
        enc = vigenere_encrypt(text, key)
        path = os.path.join(out_dir, f'encrypted {key_len}.txt')
        with open(path, 'w', encoding='utf-8') as out:
            out.write(enc)
        ic = index_of_coincidence(enc)
        results.append((key_len, ic))

    print("\n=== ІНДЕКС ВІДПОВІДНОСТІ ДЛЯ РІЗНИХ ДОВЖИН КЛЮЧА ===")
    print(f"{'Довжина':<10} | {'IC':>15}")
    print("-" * 28)
    for l, ic in results:
        print(f"{l:<10} | {ic:>15.10f}")
    print("-" * 28)

    x, y = zip(*results)
    plt.plot(x, y, marker='o', label='IC шифртексту')
    plt.axhline(y=0.055, color='red', linestyle='--', label='IC відкритого тексту')
    plt.title("Індекс відповідності залежно від довжини ключа")
    plt.xlabel("Довжина ключа (r)")
    plt.ylabel("IC")
    plt.legend()
    plt.grid()
    plt.show()
