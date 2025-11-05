#pip install -r requirements.txt
import re
import pandas as pd
import openpyxl 
from itertools import product, permutations
import os

def read_text(io_dir, filename):
    path = os.path.join(io_dir, filename)
    f = open(path, "r", encoding="utf-8")
    text = f.read()
    f.close()
    return text

def filt_text(text, io_dir, filename = "text.txt"):
    text = re.sub(r"[^а-яА-ЯёЁ]+", "", text) # очистимо текст від зайвих символів
    text = text.lower()
    text = text.replace("ё", "е")
    text = text.replace("ъ", "ь")

    clean_filename = "clean_" + filename
    path = os.path.join(io_dir, clean_filename)
    f = open(path, "w", encoding="utf-8")
    f.write(text)
    f.close()

    return text

def gcd(a, b):
    while b > 0:
        # q = a // b
        r = a % b
        a, b = b, r
    return a

def find_inverse_element(a, m):
    # r=a*u+m*v, u - коефіцієнт біля a, v - коефіцієнт біля m
    u0, u1 = 0, 1 
    v0, v1 = 1, 0

    m_init = m # зберігаємо значення модуля перед перевизначенням в операціях
    while a > 0:
        q = m // a # 13/5 = 2
        r = m % a # 13 - 2 * 5 = 3
        # -> 13 = 2 * 5 + 3

        m, a = a, r # 5, 2 (наступний крок, зносимо a і r)

        next_u0 = u1
        next_v0 = v1
        # 3 = (13*0 + 5*1) - 2*(13*1 + 5*0)
        u1= u0 - q * u1 #0 -2*1 = -2, коеф. біля a
        v1 = v0 - q* v1 # 1-2*0 = 1, коеф. біля m
        # 3 = -2 * 5 + 1 * 13

        # оновлюємо початкові коефіцієнти для наступного кроку
        u0, v0 = next_u0, next_v0

    if m != 1:
        return None
    else:
        return u0 % m_init # повертаємо коеф. біля a за модулем m (u0, тому що останній крок 0 = u*0 +v*m, а треба 1=ua+vm)

def linear_comparison(a, b, m):
    if a < 0:
        a %= m
    if b < 0:
        b %= m

    d = gcd(a, m)

    if d == 1:
        inv_a = find_inverse_element(a, m)
        if inv_a is None:
            return None
        
        x0 = (inv_a * b) % m
        return [x0]
    
    # d > 1
    if b % d != 0:
        return None # розв'язків не існує
    
    a1 = a // d
    b1 = b // d
    m1 = m // d

    inv_a1 = find_inverse_element(a1, m1)
    if inv_a1 is None:
        return None
    
    x0 = (inv_a1 * b1) % m1

    solutions = []
    for i in range(d):
        solution = (x0 + i * m1) % m
        solutions.append(solution)
    return solutions

def count_ngrams(text, alphabet, n = 2, overlap=False):
    total_count = 0
    counts = {}

    # ініціалізуємо словник n-грам розміру alphabet^n
    for ngram in product(alphabet, repeat=n): # декартів добуток alphabet на alphabet n разів (для n=2 це aa, аб...)
        ngram = ''.join(ngram)
        counts[ngram] = 0

    # з перетинами
    if overlap:
        for i in range(len(text) - (n-1)): # n = 2, любовь - лю юб бо ов вь
            ngram = text[i:i+n]
            counts[ngram] += 1
            total_count += 1

    # без перетинів
    else:
        cutted_len_text = len(text) - (len(text) % n)
        for i in range(0, cutted_len_text - (n-1), n): # n = 2, любовь - лю бо вь
            ngram = text[i:i+n]
            counts[ngram] += 1
            total_count += 1

    return counts, total_count

def freq_ngrams(counts, total_count):
    freqs = {}
    for ngram in counts:
        freqs[ngram] = (counts[ngram]/total_count)
    
    return freqs

def dict_visualization(output_dir, dct, columns, sort):
    df = pd.DataFrame(list(dct.items()), columns=columns)
    if sort:
        df = df.sort_values(by=columns[1], ascending=False).reset_index(drop=True)
    print(df.head(5).round(4).to_string(index=False))
    print()
    
    path = os.path.join(output_dir, f"{columns[1]}By{columns[0]}.xlsx")
    df.to_excel(path, index=False)
    return df["Bigram"].head(5).tolist() # повертаємо список 5-ти найчастіших біграм

def bigram_to_num(bigram, alphabet, n):
    x1 = alphabet.index(bigram[0])
    x2 = alphabet.index(bigram[1]) 
    return x1 * n + x2 # X = x1*n + x2, Y = y1*n + y2

def num_to_bigram(bigram, alphabet, n):
    b1 = bigram // n 
    b2 = bigram % n
    return alphabet[b1] + alphabet[b2]

def afinne_decrypt(cipher, a, b, alphabet):
    n = len(alphabet)
    m = n**2

    bigrams = []
    for i in range(0, len(cipher)-1, 2):
        Y_bigram = cipher[i:i+2]
        
        Y = bigram_to_num(Y_bigram, alphabet, n)

        # Припускаємо, що той, хто шифрував повідомлення, не використовував ключ, який допускає неоднозначність розшифрування
        # Тому, що, наприклад, при неоднозначності 3-ьох біграм з 2-ма розв'язками, у нас, відповідно, буде 6 варіацій розшифрування
        if gcd(a, m) != 1: # у нас не буде кількох розв'язків, якщо a і m - взаємнопрості
            return None
        
        X = linear_comparison(a, Y - b, m)[0] # беремо перший елемент, бо ф-ція повертає список
        X_bigram = num_to_bigram(X, alphabet, n)
        bigrams.append(X_bigram)

    decrypted = "".join(bigrams)
    return decrypted

def afinne_key_freq_decrypt(X1_bigram, X2_bigram, Y1_bigram, Y2_bigram, alphabet):
    n = len(alphabet)
    m = n**2

    X1 = bigram_to_num(X1_bigram, alphabet, n)
    X2 = bigram_to_num(X2_bigram, alphabet, n)
    Y1 = bigram_to_num(Y1_bigram, alphabet, n)
    Y2 = bigram_to_num(Y2_bigram, alphabet, n)

    a_solutions = linear_comparison(X1-X2, Y1-Y2, m) # a = (X1-X2)^-1 * (Y1-Y2) % n**2 
    if a_solutions == None:
        return None
    keys = []
    for a in a_solutions: # для кожного значення a рахуємо значення b
        b = (Y1 - a * X1) % m
        keys.append([a, b])
    return keys

def rus_lang_detector(text, forbidden_bigrams, top_lang_bigrams, freq_letters_lang, alphabet):
    counts_m, total_count_m = count_ngrams(text, alphabet, n=1)
    freqs_m = freq_ngrams(counts_m, total_count_m)
    counts_b, total_count_b = count_ngrams(text, alphabet, n=2, overlap=True)
    freqs_b = freq_ngrams(counts_b, total_count_b)

    #Критерій заборонених l-грам
    count_forbidden = 0
    for bigram in forbidden_bigrams:
        freq = freqs_b[bigram]
        if freq > 0.001:
            count_forbidden += 1
    
    if count_forbidden >= 2: # до прикладу ми аналізуємо текст довжини 1001 символу. Одна описка ОК, дві НЕ ОК
        return False
    
    #Критерій частих l-грам
    sorted_freqs = sorted(freqs_b.items(), key=lambda x: x[1], reverse=True)[:5]

    top_text_bigrams = []
    for i in range(len(sorted_freqs)):
        freq = sorted_freqs[i]
        bigram = freq[0]
        top_text_bigrams.append(bigram)
    
    count_top_lang = 0
    for bigram in top_text_bigrams:
        if bigram in top_lang_bigrams:
            count_top_lang += 1

    if count_top_lang < 2:
        return False

    # Перевірка частот частих літер
    # Гіпотеза: сумарна частота 5-ти найчастіших літер в мові - 41%. Відповідно, частота цих літер в тексті буде +-20% від частоти в мові (33-49%)
    sorted_lang = sorted(freq_letters_lang.items(), key=lambda x: x[1], reverse=True)

    top5_lang_sum = 0
    for i in range(5):
        top5_lang_sum += sorted_lang[i][1]

    sorted_text = sorted(freqs_m.items(), key=lambda x: x[1], reverse=True)
    top5_text_sum = 0
    for i in range(5):
        top5_text_sum += sorted_text[i][1]

    low= top5_lang_sum * 0.8
    high = top5_lang_sum * 1.2

    if low > top5_text_sum or high < top5_text_sum:
        return False

    return True

def main():
    # літери ьы поміняні місцями, відповідно до їх розміщення в алфавіті, оскільки шифротекст, як виявилось, чомусь має такий порядок букв
    alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя" 
    input_dir = "input"
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if not os.path.exists(input_dir):
        os.mkdir(input_dir)
        print(f"папка {input_dir} порожня, будь-ласка, помістіть в неї файли для обробки")

    filename = "11.txt"
    text = read_text(input_dir, filename)
    text = filt_text(text, output_dir, filename)
    print(f"ШТ: {text[:80]}...\n")

    counts, total_count = count_ngrams(text, alphabet, n=2)
    freqs = freq_ngrams(counts, total_count)

    top_ct_bigrams= dict_visualization(output_dir, freqs, ["Bigram", "Freq"], sort=True)
    top_lang_bigrams = ["ст", "но", "то", "на", "ен"]

    all_keys = []
    for b_x1, b_x2 in permutations(top_lang_bigrams, 2):
        for b_y1, b_y2 in permutations(top_ct_bigrams, 2):
            keys = afinne_key_freq_decrypt(b_x1, b_x2, b_y1, b_y2, alphabet)

            print(f"Ключі (X={b_x1}, {b_x2} | Y={b_y1}, {b_y2}):")
            if not keys:
                print("Відсутні\n")
                continue

            i=0
            for a, b in keys:
                i+=1
                print(f"{i}: a = {a:4d},  b = {b:4d}")
                if [a, b] not in all_keys:
                    all_keys.append([a, b])
            print()

    print(f"Знайдено {len(all_keys)} ключів\n")

    forbidden_bigrams = ["аь", "оь", "еь", "иь", "ыь", "эь", "юь", "яь","ьь", "йь", "ьй", "ьы", "яы"]
    freq_letters_lang = {'о': 0.1148, 'е': 0.0867, 'а': 0.0757, 'н': 0.0673, 'и': 0.0631, 'т': 0.0621, 'с': 0.057, 'л': 0.0491, 'в': 0.0427,
                        'р': 0.0424, 'м': 0.036, 'к': 0.034, 'д': 0.0312, 'у': 0.0283, 'п': 0.0264, 'я': 0.0216, 'ы': 0.019, 'ь': 0.0188,
                        'г': 0.0175, 'з': 0.0166, 'б': 0.0164, 'ч': 0.0156, 'й': 0.0118, 'ж': 0.0102, 'х': 0.0091, 'ш': 0.0082, 'ю': 0.0056,
                        'э': 0.0046, 'ц': 0.0031, 'щ': 0.0031, 'ф': 0.0016, 'ъ': 0.0003}
    
    result = []
    print("Розшифрування за знайденими ключами та аналіз на відповідність текстів російській мові...")
    for a, b in all_keys:
        dec_text = afinne_decrypt(text, a, b, alphabet)
        #print(f"ВТ: {dec_text[:80]}...\n")

        detect = rus_lang_detector(dec_text, forbidden_bigrams, top_lang_bigrams, freq_letters_lang, alphabet)
        if detect:
            print(f"Виявлено потенційний текст: {dec_text[:55]}...\n")
            result.append([dec_text, a, b])
    
    if len(result) == 1:
        res_text = result[0][0]
        a = result[0][1]
        b = result[0][2]
        print(f"ШТ УСПІШНО РОЗШИФРОВАНО!\nВТ:{res_text}...")
        print(f"Ключ: ({a}, {b})")

        path = os.path.join(output_dir, f"decrypted_{filename}")
        f = open(path, "w", encoding="utf-8")
        f.write(result[0])
        f.write(f"k = ({a}, {b})")
        f.close()

if __name__ == "__main__":
    main()
