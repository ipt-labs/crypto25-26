import re
from collections import Counter
import itertools
import math


def read_ciphertext(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def get_bigrams(text):
    bigrams = [text[i:i+2] for i in range(len(text) - 1)]
    return Counter(bigrams)


def letter_frequency_check(text):
    letter_frequencies = Counter(text)
    common_letters = ['о', 'а', 'е']
    rare_letters = ['ф', 'щ', 'ь']
    
    
    common_freq = sum(letter_frequencies[letter] for letter in common_letters) / len(text)
    rare_freq = sum(letter_frequencies[letter] for letter in rare_letters) / len(text)
    
    
    return common_freq > 0.3 and rare_freq < 0.05


def decrypt_text(ciphertext, key):
    decrypted_text = ""
    for char in ciphertext:
        if char in key:
            decrypted_text += key[char]
        else:
            decrypted_text += char
    return decrypted_text


def generate_candidates(common_bigrams, ciphertext_bigrams):
    candidates = []
    for common_bigram, cipher_bigram in itertools.product(common_bigrams, ciphertext_bigrams):
        
        key = {cipher_bigram[0]: common_bigram[0], cipher_bigram[1]: common_bigram[1]}
        candidates.append(key)
    return candidates


def decrypt_and_validate(ciphertext, common_bigrams, frequent_bigrams):
    
    ciphertext_bigrams = get_bigrams(ciphertext)

    
    candidates = generate_candidates(common_bigrams, ciphertext_bigrams)

    for candidate in candidates:
        
        decrypted_text = decrypt_text(ciphertext, candidate)

        
        if letter_frequency_check(decrypted_text):
            print(f"Знайдений можливий ключ: {candidate}")
            print(f"Дешифрований текст: {decrypted_text[:500]}") 
            break


common_bigrams = ["ст", "но", "то", "на", "ен"]


ciphertext = read_ciphertext("C:/Users/godro/OneDrive/Desktop/3lab/05.txt")

ciphertext = re.sub(r'[^а-яА-Я ]', '', ciphertext.lower())  


decrypt_and_validate(ciphertext, common_bigrams, get_bigrams(ciphertext))
