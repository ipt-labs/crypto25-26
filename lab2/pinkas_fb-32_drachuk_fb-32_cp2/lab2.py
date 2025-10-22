#pip install -r requirements.txt
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl 
import numpy as np
import os

def read_text(io_dir, filename):
    f = open(f"{io_dir}\\{filename}", "r", encoding="utf-8")
    text = f.read()
    f.close()
    return text

def filt_text(text, io_dir, filename = "text.txt"):
    text = re.sub(r"[^а-яА-ЯёЁ]+", "", text) # очистимо текст від зайвих символів
    text = text.lower()
    text = text.replace("ё", "е")

    clean_filename = "clean_" + filename
    f = open(f"{io_dir}\\{clean_filename}", "w", encoding="utf-8")
    f.write(text)
    f.close()

    return text

def vigenere_encrypt(message, key, alphabet):
    n = len(alphabet)

    k = []
    for char in key:
        if char not in alphabet:
            raise ValueError(f"Символ '{char}' у ключі '{key}' не входить до алфавіту")
        k.append(alphabet.index(char))

    r = len(k)

    msg = []
    for char in message:
        if char not in alphabet:
            raise ValueError(f"Символ '{char}' у тексті '{message[:10]}...' не входить до алфавіту")
        msg.append(alphabet.index(char))

    ciph = []
    for i in range(len(msg)):
        ciph_i = (msg[i] + k[i%r]) % n # y_i = (x_i+k_imodr)modn
        ciph.append(ciph_i)

    encrypted_list = []
    for i in ciph:
        encrypted_list.append(alphabet[i])

    encrypted_message = "".join(encrypted_list)

    return encrypted_message

def vigenere_decrypt(cipher, key, alphabet):
    n = len(alphabet)

    k = []
    for char in key:
        if char not in alphabet:
            raise ValueError(f"Символ '{char}' у ключі '{key}' не входить до алфавіту")
        k.append(alphabet.index(char))

    r = len(k)

    ciph = []
    for char in cipher:
        if char not in alphabet:
            raise ValueError(f"Символ '{char}' у шифротексті '{cipher[:10]}...' не входить до алфавіту")
        ciph.append(alphabet.index(char))

    msg = []
    for i in range(len(ciph)):
        msg_i = (ciph[i] - k[i%r]) % n # x_i = (y_i-k_imodr)modn
        msg.append(msg_i)

    decrypted_list = []
    for i in msg:
        decrypted_list.append(alphabet[i])

    decrypted_message = "".join(decrypted_list)

    return decrypted_message

def count_letters(text, alphabet):
    total_count = 0
    counts = {}

    for ch in alphabet:
        counts[ch] = 0 # ініціалізація

    for ch in text:
        if ch in counts:
            counts[ch] += 1
            total_count += 1

    return counts, total_count

def index_of_coincidence(text, alphabet): # I(Y) = sum_t(N_t(Y) * (N_t(Y)-1)) / (n (n-1)), t є Zm
    counts, n = count_letters(text, alphabet)

    s = 0
    for N_t in counts.values():
        s += N_t * (N_t - 1)

    ic = s / (n * (n - 1))
    return ic

def symbol_match_by_rank(text, r): # D_r = sum_i(δ(y_i,y_i+1)), i є [1, n-r] 
    n = len(text)
    D_r = 0

    for i in range(n - r):
        if text[i] == text[i + r]:
            D_r += 1  # δ(a,b) = 1, якщо символи збігаються

    return D_r

def dict_visualization(output_dir, dct, columns, title, yrange=[0, 0.06, 0.005]):
    df = pd.DataFrame(list(dct.items()), columns=columns)
    print(f"{df.to_string(index=False)}\n")
    df.to_excel(f"{output_dir}\\{columns[1]}By{columns[0]}.xlsx", index=False)

    # Порівняємо графічно
    plt.figure()
    sns.barplot(data=df, x=columns[0], y=columns[1], color="skyblue")
    plt.title(title)
    plt.xlabel(columns[0])
    plt.ylabel(columns[1])

    plt.xticks(rotation=45)
    plt.yticks(np.arange(yrange[0], yrange[1], yrange[2]))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}\\{columns[1]}By{columns[0]}.png", dpi=300)

def vigenere_key_freq_decrypt(message, KeyLen, letter_x, alphabet):
    n = len(alphabet)

    abc = {}
    for char in alphabet:
        abc[char] = alphabet.index(char)

    k = []
    for i in range(KeyLen):
        y = message[i::KeyLen]

        counts, total = count_letters(y, alphabet)
        if total == 0:
            print(f"[COL {i}] Порожній стовпчик → ki=0")
            k.append(0)
            continue

        max_letter_y = max(counts, key=counts.get) # y* (якщо в кількість букви максимальна, то, відповідно, і частота теж)

        ki = (abc[max_letter_y] -  abc[letter_x]) % n
        k.append(ki)
    
    letters = []
    for ki in k:
        letter = alphabet[ki]
        letters.append(letter)

    key = ''.join(letters)

    return key

def main():
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    input_dir = "input"
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if not os.path.exists(input_dir):
        os.mkdir(output_dir)
        print(f"папка {input_dir} порожня, будь-ласка, помістіть в неї файли для обробки")

    # PART 1
    filename = "Nekrasov_Zelenyu_shum.txt"
    text = read_text(input_dir, filename)
    text = filt_text(text, output_dir, filename)
    print(f"ВТ: {text[:80]}...\n")
    
    keys = ["он","код", "свет", "весна", "добродушно", "улыбнисьнам", "солнцевнутри", "кошачьямилота", "улыбайсяпочаще", "чудноемгновение", 
            "шестьдесятдевять", "радостькаждогодня", "ловичудесныймомент", "пустьденьбудетярким", "пустьденьбудеттеплым"]

    f = open(f"{output_dir}\\encrypted_{filename}", "w", encoding="utf-8")
    f.write(f"ВТ: {text}\n\n")

    enc_texts = {}
    for k in keys:
        n = len(k)
        if n in enc_texts: # будемо скіпати ключі, довжини яких вже були
            continue
        enc = vigenere_encrypt(text, k, alphabet)
        print(f"K: {k}")
        print(f"ШТ: {enc[:80]}...\n")
        enc_texts[n] = enc

        f.write(f"К: {k}\n")
        f.write(f"ШТ: {enc}\n\n")

    f.close()

    indexes_of_coincidence = {}
    indexes_of_coincidence["0(ВТ)"] = index_of_coincidence(text, alphabet) # I(Y) ВТ

    for k, enc_text in enc_texts.items():
        indexes_of_coincidence[k] = index_of_coincidence(enc_text, alphabet)
    
    dict_visualization(output_dir, indexes_of_coincidence, ["KeyLens", "IC"], "Index Of Coincidence for different key lens", [0, 0.06, 0.005])

    # PART 2
    filename2 = "var11.txt"
    ct = read_text(input_dir, filename2)
    #ОПЦІОНАЛЬНО
    #ct = filt_text(ct, output_dir, filename2)

    symbol_matches_by_ranks = {}
    for r in range(1, 33):
        symbol_matches_by_ranks[r] = symbol_match_by_rank(ct, r)

    dict_visualization(output_dir, symbol_matches_by_ranks, ["Rank", "SymbolMatch"], "Symbol match for different ranks", [0, 500, 50])
    
    KeyLen = max(symbol_matches_by_ranks, key=symbol_matches_by_ranks.get) # шукана довжина ключа
    print(f"Знайдено довжину ключа: {KeyLen}")

    freq_dict = {'о': 0.1148, 'е': 0.0867, 'а': 0.0757, 'н': 0.0673, 'и': 0.0631, 'т': 0.0621, 'с': 0.057, 'л': 0.0491, 'в': 0.0427,
                'р': 0.0424, 'м': 0.036, 'к': 0.034, 'д': 0.0312, 'у': 0.0283, 'п': 0.0264, 'я': 0.0216, 'ы': 0.019, 'ь': 0.0188,
                'г': 0.0175, 'з': 0.0166, 'б': 0.0164, 'ч': 0.0156, 'й': 0.0118, 'ж': 0.0102, 'х': 0.0091, 'ш': 0.0082, 'ю': 0.0056,
                'э': 0.0046, 'ц': 0.0031, 'щ': 0.0031, 'ф': 0.0016, 'ъ': 0.0003}

    freq_top3 = []
    for ch in list(freq_dict)[:3]:
        freq_top3.append(ch)

    for letter in freq_top3:
        key = vigenere_key_freq_decrypt(ct, KeyLen, letter, alphabet)
        print(f"Ключ (найчастіша літера - {letter}): {key}")
    
    key = "венецианскийкупец" # за правилами мови об'єднали ключі з найчастішими літерами о, е
    print(f"Отримали ключ: {key}")

    dec_ct = vigenere_decrypt(ct, key, alphabet)
    print(f"ШТ: {ct[:80]}...")
    print(f"ВТ: {dec_ct[:80]}...")

    f = open(f"{output_dir}\\decrypted_{filename2}", "w", encoding="utf-8")
    f.write(f"ШТ: {ct}\n")
    f.write(f"К: {key}\n")
    f.write(f"ВТ: {dec_ct}\n")

    plt.show() # відобразимо наші графіки
    
    
if __name__ == "__main__":
    main()