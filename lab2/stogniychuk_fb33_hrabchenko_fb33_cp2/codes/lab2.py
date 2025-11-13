import re
import matplotlib.pyplot as plt

alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def clean_text(input_text):
    """Очищення тексту від небуквених символів та пробілів"""
    text = input_text.lower()
    text = text.replace('ё', 'е')
    text = re.sub(r'[^а-яА-ЯёЁ ]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

def vigenere_cipher(message, key_word):
    """Шифрування методом Віженера"""
    global alphabet
    result = []
    key_len = len(key_word)

    for i, symbol in enumerate(message):
        if symbol in alphabet:
            m_index = alphabet.index(symbol)
            k_index = alphabet.index(key_word[i % key_len])
            new_char = alphabet[(m_index + k_index) % len(alphabet)]
            result.append(new_char)
        else:
            result.append(symbol)
    
    return ''.join(result)

def coincidence_index(text):
    """Розрахунок індексу відповідності"""
    n = len(text)
    counts = {ch: text.count(ch) for ch in set(text)}
    return sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))

def write_results(filename, clean_text, encrypted_variants, used_keys):
    """Збереження результатів у файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Очищений текст:\n")
        f.write(clean_text + "\n\n")
        f.write("Результати шифрування методом Віженера:\n")
        f.write("=" * 150 + "\n")

        for i, key in enumerate(used_keys):
            f.write(f"\nКлюч: {key} (довжина: {len(key)})\n")
            f.write(f"Шифротекст: {encrypted_variants[i]}\n")
            f.write("=" * 150 + "\n")

def visualize_indices(keys, indices):
    """Побудова графіка залежності індексу відповідності від довжини ключа"""
    lengths = [len(k) for k in keys]
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(lengths)), indices, color=plt.cm.tab10.colors[:len(lengths)], alpha=0.8)
    plt.xlabel('Довжина ключа')
    plt.ylabel('Індекс відповідності')
    plt.xticks(range(len(lengths)), lengths)
    plt.title('Залежність індексу відповідності від довжини ключа')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.show()

def execute(path):
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    prepared = clean_text(source)

    key_list = [
        "он", "мор", "кожа", "кровь", "забастовка",
        "вдохновитель", "беззаботность", "абсорбированый", "антикоммунистический"
    ]

    encrypted_versions = []
    indices = []

    for key in key_list:
        ciphered = vigenere_cipher(prepared, key)
        encrypted_versions.append(ciphered)
        indices.append(coincidence_index(ciphered))
        print(f"\nКлюч: {key} (довжина: {len(key)})")
        print(f"Шифротекст: {ciphered}")
        print("=" * 150)

    original_ic = coincidence_index(prepared)
    print(f"\nІндекс відповідності для відкритого тексту: {original_ic:.6f}\n")

    print("Індекси відповідності для зашифрованих текстів:")
    print("-" * 100)
    print(f"{'Ключ':<25} {'Довжина':<15} {'Індекс відповідності':<20}")
    print("-" * 100)
    for key, ic in zip(key_list, indices):
        print(f"{key:<25} {len(key):<15} {ic:.6f}")
    print("-" * 100)

    write_results("results_lab2.txt", prepared, encrypted_versions, key_list)
    visualize_indices(key_list, indices)


file_path = "c:\\Users\\u1208\\OneDrive\\Робочий стіл\\5 сем\\lab2crypto\\lab2\\mm.txt"
execute(file_path)

