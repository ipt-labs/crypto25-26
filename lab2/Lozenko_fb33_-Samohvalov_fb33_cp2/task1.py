import re
from collections import Counter
import matplotlib.pyplot as plt  # <-- Додано імпорт для графіків

# Український алфавіт (33 літери)
UKR_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
ALPHABET_LEN = len(UKR_ALPHABET)

def vigenere_encrypt(plaintext: str, key: str) -> str:
    """Шифрує текст шифром Віженера, зберігаючи регістр та символи."""
    ciphertext = []
    key_len = len(key)
    key_index = 0
    key_lower = key.lower()

    for char in plaintext:
        if char.lower() in UKR_ALPHABET:
            is_upper = char.isupper()
            p_idx = UKR_ALPHABET.find(char.lower())
            k_char = key_lower[key_index % key_len]
            k_idx = UKR_ALPHABET.find(k_char)
            
            c_idx = (p_idx + k_idx) % ALPHABET_LEN
            
            new_char = UKR_ALPHABET[c_idx]
            ciphertext.append(new_char.upper() if is_upper else new_char)
            key_index += 1
        else:
            ciphertext.append(char)
            
    return "".join(ciphertext)

def calculate_ic(text: str) -> float:
    """Розраховує індекс відповідності (IC)."""
    
    cleaned_text = "".join(char for char in text.lower() if char in UKR_ALPHABET)
    N = len(cleaned_text)
    if N < 2:
        return 0.0

    counts = Counter(cleaned_text)
    numerator = sum(count * (count - 1) for count in counts.values())
    denominator = N * (N - 1)
    
    return numerator / denominator

def plot_ic_dependency(key_lengths, ic_values, ic_plaintext):
    """
    Будує графік залежності IC від довжини ключа r.
    """
    plt.figure(figsize=(10, 6))
    
    # Графік для шифротекстів
    plt.plot(key_lengths, ic_values, 'bo-', label='IC Шифротексту (залежно від r)')
    
    # Горизонтальні лінії для порівняння
    plt.axhline(y=ic_plaintext, color='g', linestyle='--', label=f'IC Відкритого тексту ({ic_plaintext:.6f})')
    
    
    plt.title('Залежність індексу відповідності (IC) від довжини ключа (r)')
    plt.xlabel('Довжина ключа (r)')
    plt.ylabel('Індекс відповідності (IC)')
    
    # Встановлюємо мітки на осі X, щоб вони відповідали нашим ключам
    plt.xticks(key_lengths)
    plt.legend()
    plt.grid(True)
    
    # Зберігаємо графік у файл
    plt.savefig('ic_dependency_graph.png')
    print("\nГрафік збережено у файл 'ic_dependency_graph.png'")
    
    # Показуємо графік
    plt.show()

def main():
    # --- 1. Завантаження тексту ---
    try:
        with open("plaintext.txt", "r", encoding="utf-8") as f:
            plaintext = f.read()
        print(f"Завантажено текст з 'plaintext.txt' (розмір: {len(plaintext)} байт)\n")
    except FileNotFoundError:
        print("ПОМИЛКА: Файл 'plaintext.txt' не знайдено.")
        return
    
    # --- 2. Завдання 1: Шифрування (Сталі ключі) ---
    fixed_keys = {
        2: "на",
        3: "три",
        4: "вода",
        5: "слово",
        10: "гарніквіти",
        12: "менезватиден",
        15: "супермегакрутий",
        18: "домашнійприступник" 
    }
    
    # Використовуємо 17, а не 15, для коректного відображення на графіку
    key_r_values = [2, 3, 4, 5, 10, 12, 15, 18] 
    keys_map = {
        2: "на",
        3: "три",
        4: "вода",
        5: "слово",
        10: "гарніквіти",
        12: "менезватиден",
        15: "супермегакрутий",
        18: "домашнійприступник" 
    }

    ciphertexts = {}
    print("--- Завдання 1: Шифрування ---")
    
    for r, key in keys_map.items():
        print(f"Ключ (r={r}): '{key}'")
        ciphertexts[r] = vigenere_encrypt(plaintext, key)
        
        filename = f"ciphertext_r{r}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(ciphertexts[r])
        print(f"Шифротекст збережено у файл: {filename}\n")

    # --- 3. Завдання 2: Індекси Відповідності (IC) ---
    print("--- Завдання 2: Індекси Відповідності (IC) ---")
    
    ic_plaintext = calculate_ic(plaintext)
    print(f"IC Відкритого тексту:   {ic_plaintext:.6f}")
    
    print("-------------------------------------------------")
    
    ic_cipher_values = [] # Список для значень IC для графіка
    
    for r in key_r_values:
        ic_cipher = calculate_ic(ciphertexts[r])
        ic_cipher_values.append(ic_cipher) # Збираємо дані
        print(f"IC Шифротексту (r={r}):  {ic_cipher:.6f}")



    # --- 4. Побудова графіка ---
    plot_ic_dependency(key_r_values, ic_cipher_values, ic_plaintext)

if __name__ == "__main__":
    main()