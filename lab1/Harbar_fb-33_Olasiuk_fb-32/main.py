import re
import math
import os
import pandas as pd
from chardet.universaldetector import UniversalDetector

ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
ALPHABET_ = "абвгдежзийклмнопрстуфхцчшщыьэюя "

def clean_text(text):
    text = text.strip().lower().replace("ё","е").replace("ъ","ь")
    text = re.sub(r'[^а-я\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    with open("clean.txt", "w", encoding="utf-8") as f:
        f.write(text)
    return text

def count_monograms(text, space=False):
    if space:
        letters = ALPHABET_
    else:
        letters = ALPHABET

    num_of_monograms = {}
    for lett in letters:
        num_of_monograms[lett] = 0

    total_num = 0
    for l in text:
        if l in num_of_monograms:
            num_of_monograms[l] += 1
            total_num += 1

    return num_of_monograms, total_num  

def count_bigrams(text, space=False, intersection=True):
    if space:
        letters = ALPHABET_
    else:
        letters = ALPHABET
    
    num_of_bigrams = {}
    for lett1 in letters:
        for lett2 in letters:
            num_of_bigrams[lett1 + lett2] = 0

    total_num = 0    
    if intersection:
        for i in range(len(text) - 1): 
            bigram = text[i] + text[i + 1]  
            if bigram in num_of_bigrams:
                num_of_bigrams[bigram] += 1
                total_num += 1
    else:
        for i in range(0, len(text) - 1, 2): 
            bigram = text[i] + text[i + 1]
            if bigram in num_of_bigrams:
                num_of_bigrams[bigram] += 1
                total_num += 1
    
    return num_of_bigrams, total_num

def frequencies(num_of, total_num):
    freq = {}
    for ngram, num in num_of.items():
        freq[ngram] = num/total_num
    return freq

def entropy(frequence):
    entropy = 0
    for freq in frequence.values():
        if freq > 0:
            entropy -= freq * math.log2(freq)
    n = len(list(frequence.keys())[0])  
    return entropy/n

def bigram_df(bigram_dict):
    letters = []
    for bigram in bigram_dict.keys():
        for letter in bigram:
            if letter not in letters:
                letters.append(letter)
    letters.sort()  
   
    data = {}
    for lett_col in letters:  
        data[lett_col] = []
        for lett_row in letters:  
            bigram = lett_row + lett_col  
            data[lett_col].append(bigram_dict[bigram])
   
    return pd.DataFrame(data, index=letters)

def redundancy(entropy, n):
	return 1 - (entropy / math.log2(n))

def calculatings(text, output_file):

    text = clean_text(text)
#---------------------------------------------------------------------------------------------------
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    num_of_monogram, total_num_of_monograms = count_monograms(text, space=False)
    num_of_monogram_sp, total_num_of_monograms_sp = count_monograms(text, space=True)
    
    num_of_bigram, total_num_of_bigrams = count_bigrams(text, space=False, intersection=False)
    num_of_bigram_sp, total_num_of_bigrams_sp = count_bigrams(text, space=True, intersection=False)
    num_of_bigram_int, total_num_of_bigrams_int = count_bigrams(text, space=False, intersection=True)
    num_of_bigram_sp_int, total_num_of_bigrams_sp_int = count_bigrams(text, space=True, intersection=True)

#-----------------------------------------------------------------------------------------------------

    monogram_freq = frequencies(num_of_monogram, total_num_of_monograms)
    monogram_freq_sp = frequencies(num_of_monogram_sp, total_num_of_monograms_sp)
    
    bigram_freq = frequencies(num_of_bigram, total_num_of_bigrams)
    bigram_freq_sp = frequencies(num_of_bigram_sp, total_num_of_bigrams_sp)
    bigram_freq_int = frequencies(num_of_bigram_int, total_num_of_bigrams_int)
    bigram_freq_sp_int = frequencies(num_of_bigram_sp_int, total_num_of_bigrams_sp_int)

#-------------------------------------------------------------------------------------------------------    

    pd.DataFrame(num_of_monogram.items(), columns=["Monogram", "Amount"]).sort_values(by="Amount", ascending=False).to_excel(writer, sheet_name="Monogram_amount")
    pd.DataFrame(num_of_monogram_sp.items(), columns=["Monogram", "Amount"]).sort_values(by="Amount", ascending=False).to_excel(writer, sheet_name="Monogram_amount_sp")
    pd.DataFrame(monogram_freq.items(), columns=["Monogram", "Frequency"]).sort_values(by="Frequency", ascending=False).to_excel(writer, sheet_name="Monogram_freq")
    pd.DataFrame(monogram_freq_sp.items(), columns=["Monogram", "Frequency"]).sort_values(by="Frequency", ascending=False).to_excel(writer, sheet_name="Monogram_freq_sp")

    bigram_df(num_of_bigram).to_excel(writer, sheet_name="Bigram_amount")
    bigram_df(num_of_bigram_sp).to_excel(writer, sheet_name="Bigram_amount_sp")
    bigram_df(num_of_bigram_int).to_excel(writer, sheet_name="Bigram_amount_int")
    bigram_df(num_of_bigram_sp_int).to_excel(writer, sheet_name="Bigram_amount_sp_int")
    bigram_df(bigram_freq).to_excel(writer, sheet_name="Bigram_freq")
    bigram_df(bigram_freq_sp).to_excel(writer, sheet_name="Bigram_freq_sp")
    bigram_df(bigram_freq_int).to_excel(writer, sheet_name="Bigram_freq_int")
    bigram_df(bigram_freq_sp_int).to_excel(writer, sheet_name="Bigram_freq_sp_int")

    writer.close()
#--------------------------------------------------------------------------------------------------------------

    H1 = entropy(monogram_freq)
    H1_sp = entropy(monogram_freq_sp)
    H2 = entropy(bigram_freq)
    H2_sp = entropy(bigram_freq_sp)
    H2_int = entropy(bigram_freq_int)
    H2_sp_int = entropy(bigram_freq_sp_int)

    R_H1 = redundancy(H1, 31)
    R_H1_sp = redundancy(H1_sp, 32)
    R_H2 = redundancy(H2, 31)
    R_H2_sp = redundancy(H2_sp, 32)
    R_H2_int = redundancy(H2_int, 31)
    R_H2_sp_int = redundancy(H2_sp_int, 32)

    H10 = (2.53007945178473 + 3.27016036564542)/2
    H20 = (2.09369203404264 + 2.74291016606417)/2
    H30 = (1.4170205694229 + 2.13972183240961)/2

    R_H10 = redundancy(H10, 32)
    R_H20 = redundancy(H20, 32)
    R_H30 = redundancy(H30, 32)

    print("=========ENTROPY=========")
    print(f"H1, {H1}")
    print(f"H1 (with spaces), {H1_sp}")
    print(f"H2, {H2}")
    print(f"H2 (with spaces), {H2_sp}")
    print(f"H2 (with intersection), {H2_int}")
    print(f"H2 (with all)), {H2_sp_int}")

    print("=========REDUNDANCY=========")
    print(f"R1-H1, {R_H1}")
    print(f"R1-H1 (with spaces), {R_H1_sp}")
    print(f"R2-H2, {R_H2}")
    print(f"R2-H2 (with spaces), {R_H2_sp}")
    print(f"R2-H2 (with intersection), {R_H2_int}")
    print(f"R2-H2 (with all)), {R_H2_sp_int}")
    print(f"R-H10, {R_H10}")
    print(f"R-H20, {R_H20}")
    print(f"R-H30, {R_H30}")


path = "fat_lion.txt"      
if not os.path.exists(path):
    print(f"File {path} not exist")
    exit()

detector = UniversalDetector()
with open(path, "rb") as f:
    for line in f:
        detector.feed(line)
        if detector.done:
            break
detector.close()
enc = detector.result.get("encoding")
if not enc:
    print("Encoding fail")
    exit()

with open(path, encoding=enc) as f:
    kaka = f.read()
    output_name = "calculatings.xlsx"
    calculatings(kaka, output_name)
