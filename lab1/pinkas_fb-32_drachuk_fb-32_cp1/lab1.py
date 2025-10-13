#pip install -r "requirements.txt"
import re
from math import log2
import pandas as pd
import openpyxl 
from itertools import product
import os

def fuilt_text_alphabet(text, alphabet, replace_yo = False, spaces = True):
    text = text.replace("\n", " ")

    text = re.sub(r"[^а-яА-ЯёЁ ]+", " ", text) 

    if spaces:
        # видаляємо зайві пробіли
        text_list = []
        prev_space = False

        for ch in text:
            if ch == " ":
                if not prev_space:
                    text_list.append(" ")
                    prev_space = True
            else:
                text_list.append(ch)
                prev_space = False

        text = "".join(text_list)
    
    else:
        text = text.replace(" ", "")
        alphabet = alphabet.replace(" ", "")

    text = text.lower()

    if replace_yo:
        text = text.replace("ё", "е")
        alphabet = alphabet.replace("ё", "")

    return text, alphabet

def count_ngrams(text, alphabet, n = 1, overlap = True):
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
        for i in range(0, len(text) - (n-1), n): # n = 2, любовь - лю бо вь
            ngram = text[i:i+n]
            if len(ngram) == n: # пропускаємо "огризки" в кінці тексту, якщо довжина тексту не кратна n
                counts[ngram] += 1
                total_count += 1

    return counts, total_count

def freq_ngrams(counts, total_count):
    freqs = {}
    for ngram in counts:
        freqs[ngram] = (counts[ngram]/total_count)
    
    return freqs

def dict_to_df(dct, columns, alphabet, sort, n, extra_dct = None):
    if n == 2: # матриця для біграм
        df = pd.DataFrame(0, index=list(alphabet), columns=list(alphabet), dtype = float)

        for bigram, value in dct.items():
            row = bigram[0]
            col = bigram[1]
            df.at[row, col] = value

        if extra_dct != None:
            extra_df = pd.DataFrame(index = list(extra_dct.keys()), data = list(extra_dct.values()), columns=list(alphabet)[:1])
            df = pd.concat([df, extra_df])

    else:
        df = pd.DataFrame(list(dct.items()), columns=columns)

        if sort:
            df = df.sort_values(by=columns[1], ascending=False).reset_index(drop=True)

        if extra_dct != None:
            extra_df = pd.DataFrame(list(extra_dct.items()), columns=columns)
            df = pd.concat([df, extra_df]).reset_index(drop=True)

    return df.round(4)

def df_to_excel(df, table_name, spaces, overlap, n):
    if spaces:
        spaces_text = "with_spaces"
    else:
        spaces_text = "w-o_spaces"
    
    if overlap:
        overlap_text = "with_overlap"
    else:
        overlap_text = "w-o_overlap"
    
    if not os.path.exists(f"{table_name}.xlsx"):
        args = {"path" : f"{table_name}.xlsx", "mode" : "w"}
    else:
        args = {"path" : f"{table_name}.xlsx", "mode" : "a", "if_sheet_exists": "replace"}

    with pd.ExcelWriter(**args) as writer:
        if n == 1:
            df.to_excel(writer, sheet_name=f"monogram_{spaces_text}", index=False)
        elif n == 2:
            df.to_excel(writer, sheet_name=f"bigram_{spaces_text}_{overlap_text}")
        else:
            df.to_excel(writer, sheet_name=f"{n}gram_{spaces_text}_{overlap_text}", index=False)

def entropy_ngrams(freqs, n):
    entropy = 0
    for freq in freqs.values():
        if freq > 0:
            entropy -= freq * log2(freq)

    entropy_norm = entropy/n
    return entropy_norm

def redundancy(entropy_norm, len_alphabet):
    redundancy = 1 - (entropy_norm/log2(len_alphabet))
    return redundancy

def process(filename, text, default_alphabet, Hn_Rn_dict, replace_yo = True, spaces = True, n = 1, overlap = True):
    if spaces:
        spaces_text = "з пробілами"
    else:
        spaces_text = "без пробілів"

    if n == 1:
        n_text = "Монограма"
        print(n_text, spaces_text)
    else:
        if n == 2:
            n_text = "Біграма"
        else:
            n_text = f"{n}-грама"

        if overlap:
            overlap_text = "з перетинами"
        else:
            overlap_text = "без перетинів"
        
        print(n_text, spaces_text, overlap_text)

    filtred_text, alphabet = fuilt_text_alphabet(text, default_alphabet, replace_yo, spaces)

    clean_filename = "clean_" + filename
    f = open(clean_filename, "w")
    f.write(filtred_text)
    f.close()

    # замінимо " " на "_" для зручності сприйняття
    filtred_text = filtred_text.replace(" ", "_")
    alphabet = alphabet.replace(" ", "_")

    counts, total_count = count_ngrams(filtred_text, alphabet, n, overlap)

    sort = True # сортувати n-граму?

    df_counts = dict_to_df(counts, ["Символ", "Кількість"], alphabet, sort, n, {"Загалом" : total_count})
    print(f"{df_counts}\n")

    freqs = freq_ngrams(counts, total_count)
    df_freqs = dict_to_df(freqs, ["Символ", "Частота"], alphabet, sort, n)
    print(f"{df_freqs}\n")

    Hn = entropy_ngrams(freqs, n)
    Rn = redundancy(Hn, len(alphabet))
    if n == 1:
        Hn_text = f"H{n} {spaces_text} = {Hn:.9f}"
        Rn_text = f"R{n} {spaces_text} = {Rn:.9f}"
    else:
        Hn_text = f"H{n} {spaces_text} {overlap_text} = {Hn:.9f}"
        Rn_text = f"R{n} {spaces_text} {overlap_text} = {Rn:.9f}"
    
    print(f"{Hn_text}")
    print(f"{Rn_text}\n")

    Hn_Rn_dict[Hn_text] = Rn_text

    # таблички
    df_to_excel(df_counts, "counts", spaces, overlap, n)
    df_to_excel(df_freqs, "frequences", spaces, overlap, n)

def main():
    default_alphabet = " абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    filename = "Sherlock_Holmes.txt"
    f = open(filename, "r")
    text = f.read()
    f.close()
    replace_yo = True
    Hn_Rn_dict = {}

    process(filename, text, default_alphabet, Hn_Rn_dict, replace_yo, spaces = False)
    process(filename, text, default_alphabet, Hn_Rn_dict, replace_yo, spaces = True)
    process(filename, text, default_alphabet, Hn_Rn_dict, replace_yo, spaces = False, n = 2)
    process(filename, text, default_alphabet, Hn_Rn_dict, replace_yo, spaces = True, n = 2)
    process(filename, text, default_alphabet, Hn_Rn_dict, replace_yo, spaces = False, n = 2, overlap = False)
    process(filename, text, default_alphabet, Hn_Rn_dict, replace_yo, spaces = True, n = 2, overlap = False)

    print("Підсумки:")
    for Hn_text, Rn_text in Hn_Rn_dict.items():
        print(Hn_text)
        print(Rn_text)

    H10_30_minmax = {1.728237391: 2.515882558, 1.67597398: 2.5012731, 1.496498052: 2.2160219086}
    
    i = 0
    for Hnmin, Hnmax in H10_30_minmax.items():
        i +=10
        Rnmin = redundancy(Hnmax, 32)
        Rnmax = redundancy(Hnmin, 32)
        print(f"{Hnmin:.9f} < H({i}) < {Hnmax:.9f}")
        print(f"{Rnmin:.9f} < R({i}) < {Rnmax:.9f}")
    
if __name__ == "__main__":
    main()
