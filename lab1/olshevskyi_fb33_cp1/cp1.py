import math

RUS_ALPHA_LOWER = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
RUS_ALPHA_UPPER = RUS_ALPHA_LOWER.upper()

def filter_russian_text(txt, allow_spaces=True):
    txt = ' '.join(txt.split())
    txt = ''.join(
        ch for ch in txt
        if ch in RUS_ALPHA_LOWER or ch in RUS_ALPHA_UPPER or (allow_spaces and ch == ' ')
    )
    return txt.lower()

def count_chars(txt):
    counts = {}
    for ch in txt:
        counts[ch] = counts.get(ch, 0) + 1
    return counts

def count_bigrams(txt):
    counts = {}
    for i in range(len(txt) - 1):
        pair = txt[i:i+2]
        counts[pair] = counts.get(pair, 0) + 1
    return counts

def count_bigrams2(txt):
    counts = {}
    for i in range(0,len(txt)-1, 2):
        pair = txt[i:i+2]
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def calculate_entropy(txt, freq_dict):
    entropy = 0.0
    length = len(txt)
    for count in freq_dict.values():
        p = count / length
        entropy += p * math.log2(p)
    return -entropy


def calculate_entropy2(txt, freq_dict):
    entropy = 0.0
    length = len(txt) - 1
    for count in freq_dict.values():
        p = count / length
        entropy += p * math.log2(p)
    return -entropy

def calculate_entropy3(txt, freq_dict):
    entropy = 0.0
    length = len(txt) / 2
    for count in freq_dict.values():
        p = count / length
        entropy += p * math.log2(p)
    return -entropy

def redundancy(entropy_val, alphabet_sz):
    return 1 - (entropy_val / math.log2(len(RUS_ALPHA_LOWER)))

def save_freq(freq_dict, txt, file_obj, heading="Частоти символів"):
    file_obj.write(f"\n=== {heading} ===\n")
    file_obj.write(f"{'Символ':<5} {'Кількість':<10} {'% від загального':<15}\n")
    length = len(txt)
    for k, v in sorted(freq_dict.items(), key=lambda x: x[1], reverse=True):
        file_obj.write(f"{k:<5} {v:<10} {v/length*100:>10.3f}%\n")

# Зчитування тексту
file_path = r"C:\Users\godro\OneDrive\Desktop\crypto\lab 1\lab1\olshevskyi_fb33_cp1\TEXT.txt"
with open(file_path, 'r', encoding='utf-8') as f:
    raw_text = f.read()

text_with_spaces = filter_russian_text(raw_text, allow_spaces=True)
text_without_spaces = filter_russian_text(raw_text, allow_spaces=False)

# Збереження очищеного тексту
with open('output_with_spaces.txt', 'w', encoding='utf-8') as f:
    f.write(text_with_spaces)
with open('output_without_spaces.txt', 'w', encoding='utf-8') as f:
    f.write(text_without_spaces)

# Частоти та ентропія
freq_with_spaces = count_chars(text_with_spaces)
freq_without_spaces = count_chars(text_without_spaces)
bigrams_with_spaces = count_bigrams(text_with_spaces)
bigrams_without_spaces = count_bigrams(text_without_spaces)
bigrams_with_spaces2 = count_bigrams2(text_with_spaces)
bigrams_without_spaces2 = count_bigrams2(text_without_spaces)


entropy_with_spaces = calculate_entropy(text_with_spaces, freq_with_spaces)
entropy_without_spaces = calculate_entropy(text_without_spaces, freq_without_spaces)
entropy_bigrams_with_spaces = calculate_entropy2(text_with_spaces, bigrams_with_spaces)/2
entropy_bigrams_without_spaces = calculate_entropy2(text_without_spaces, bigrams_without_spaces)/2
entropy_bigrams_with_spaces2 = calculate_entropy3(text_with_spaces, bigrams_with_spaces2)/2
entropy_bigrams_without_spaces2 = calculate_entropy3(text_without_spaces, bigrams_without_spaces2)/2

# Вивід у файл
with open('analysis_results.txt', 'w', encoding='utf-8') as f:
    save_freq(freq_with_spaces, text_with_spaces, f, "Літери з пробілами ")
    save_freq(freq_without_spaces, text_without_spaces, f, "Літери без пробілів ")
    save_freq(bigrams_with_spaces, text_with_spaces, f, "Біграми з пробілами ")
    save_freq(bigrams_without_spaces, text_without_spaces, f, "Біграми без пробілів ")
    save_freq(bigrams_with_spaces2, text_with_spaces, f, "Біграми з пробілами 2")
    save_freq(bigrams_without_spaces2, text_without_spaces, f, "Біграми без пробілів 2")
    f.write(f"\nЕнтропія літер з пробілами: {entropy_with_spaces:.4f}\n")
    f.write(f"Ентропія літер без пробілів: {entropy_without_spaces:.4f}\n")
    f.write(f"Ентропія біграм з пробілами: {entropy_bigrams_with_spaces:.4f}\n")
    f.write(f"Ентропія біграм без пробілів: {entropy_bigrams_without_spaces:.4f}\n")
    f.write(f"Ентропія біграм з пробілами: {entropy_bigrams_with_spaces2:.4f}\n")
    f.write(f"Ентропія біграм без пробілів: {entropy_bigrams_without_spaces2:.4f}\n")

    f.write(f"\nНадлишковість літер з пробілами: {redundancy(entropy_with_spaces, 34):.4f}\n")
    f.write(f"Надлишковість літер без пробілів: {redundancy(entropy_without_spaces, 33):.4f}\n")
    f.write(f"Надлишковість біграм з пробілами: {redundancy(entropy_bigrams_with_spaces, 34**2):.4f}\n")
    f.write(f"Надлишковість біграм без пробілів: {redundancy(entropy_bigrams_without_spaces, 33**2):.4f}\n")
    f.write(f"Надлишковість біграм з пробілами: {redundancy(entropy_bigrams_with_spaces2, 34**2):.4f}\n")
    f.write(f"Надлишковість біграм без пробілів: {redundancy(entropy_bigrams_without_spaces2, 33**2):.4f}\n")