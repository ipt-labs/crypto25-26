import os
import re
from collections import Counter
import matplotlib.pyplot as plt
from tabulate import tabulate

ALPH = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def normalize(text):
    text = text.lower().replace('ё', 'е')
    return re.sub(r'[^а-я]', '', text)

def vigenere_encrypt(text, key):
    res = []
    key_nums = [ALPH.index(ch) for ch in key]
    for i, ch in enumerate(text):
        if ch in ALPH:
            res.append(ALPH[(ALPH.index(ch) + key_nums[i % len(key_nums)]) % len(ALPH)])
    return ''.join(res)

def index_of_coincidence(text):
    n = len(text)
    if n < 2:
        return 0
    freq = Counter(text)
    return sum(v * (v - 1) for v in freq.values()) / (n * (n - 1))

def save(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    src = "text.txt"
    out_dir = "encrypted_texts"
    os.makedirs(out_dir, exist_ok=True)

    text = normalize(read(src))
    save(os.path.join(out_dir, 'plaintext.txt'), text)

    plain_ic = index_of_coincidence(text)

    keys = {
        2: 'до',
        3: 'мир',
        4: 'паро',
        5: 'судак',
        6: 'гудзон',
        7: 'канцлер',
        8: 'континет',
        9: 'деклараци',
        10: 'председате',
        11: 'выборыместо',
        12: 'разработкиая',
        13: 'соединенныеяя',
        14: 'законодательны',
        15: 'управлениеприбл',
        16: 'инстанцияштатаха',
        17: 'передвижениесреда',
        18: 'пароходноесообщени',
        19: 'независимостисоюзом',
        20: 'партнерстволюдейтами'
    }

    results = [{'r': 0, 'key': 'відкритий текст', 'IC': plain_ic}]
    for r, key in keys.items():
        encrypted = vigenere_encrypt(text, key)
        save(os.path.join(out_dir, f'vigenere_r{r}.txt'), encrypted)
        results.append({'r': r, 'key': key, 'IC': index_of_coincidence(encrypted)})

    table = [[res['r'], res['key'], f"{res['IC']:.6f}"] for res in results]
    print(tabulate(table, headers=["r (довжина ключа)", "Ключ", "Індекс відповідності"], tablefmt="fancy_grid"))

    lengths = [res['r'] for res in results]
    ics = [res['IC'] for res in results]

    plt.figure(figsize=(12,6))
    plt.bar(lengths, ics, color='skyblue', label='Індекс шифртексту')
    plt.axhline(y=plain_ic, color='red', linestyle='--', label='IC відкритого тексту')
    plt.title('Залежність індексу відповідності від довжини ключа (шифр Віженера)')
    plt.xlabel('Довжина ключа (r)')
    plt.ylabel('Індекс відповідності')
    plt.xticks(lengths)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()
