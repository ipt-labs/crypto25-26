import unicodedata
import re
from collections import Counter, defaultdict
import math
import pandas as pd
import time

def calculate_entropy(values):
    total_count = sum(values)
    return -sum((count / total_count) * math.log2(count / total_count) for count in values)

with open("text.txt", "r", encoding="utf8") as file:
    raw_text = file.read()

# С пробелами :3
text_sp = re.sub(r'[^а-яА-Я ]', '', raw_text).lower()
letters_sp = Counter(text_sp)
sorted_letters_sp = sorted(
    [(char, count, count / len(text_sp)) for char, count in letters_sp.items()],
    reverse=True, key=lambda x: x[1]
)

print("Sorted letter frequency with spaces:")
print("(letter, count, frequency)")
for letter, count, frequency in sorted_letters_sp:
    print(letter, count, frequency)

bigrams_n_sp = defaultdict(int)
for i in range(0, len(text_sp) - 1, 2):
    bigrams_n_sp[text_sp[i:i+2]] += 1

bigrams_o_sp = defaultdict(int)
for i in range(len(text_sp) - 1):
    bigrams_o_sp[text_sp[i:i+2]] += 1

print("\nH1 (entropy of single letters):", calculate_entropy(letters_sp.values()))
print("H2 (entropy of bigrams without overlapping):", calculate_entropy(bigrams_n_sp.values()) / 2)
print("H2 (entropy of bigrams with overlapping):", calculate_entropy(bigrams_o_sp.values()) / 2)

unique_sp = sorted(letters_sp.keys())
total_n = sum(bigrams_n_sp.values())
matrix_n_sp = pd.DataFrame(0.0, index=unique_sp, columns=unique_sp)
for bigram, freq in bigrams_n_sp.items():
    first_letter, second_letter = bigram[0], bigram[1]
    matrix_n_sp.at[first_letter, second_letter] = freq / total_n

print("\nBigram frequency matrix without overlapping:")
print(matrix_n_sp)
matrix_n_sp.to_csv('matrix_n_sp.csv', index=True)
time.sleep(2)

total_o = sum(bigrams_o_sp.values())
matrix_o_sp = pd.DataFrame(0.0, index=unique_sp, columns=unique_sp)
for bigram, freq in bigrams_o_sp.items():
    first_letter, second_letter = bigram[0], bigram[1]
    matrix_o_sp.at[first_letter, second_letter] = freq / total_o

print("\nBigram frequency matrix with overlapping:")
print(matrix_o_sp)
matrix_o_sp.to_csv('matrix_o_sp.csv', index=True)


# Без пробелов :D
text_ns = re.sub(r'[^а-яА-Я]', '', raw_text).lower()
letters_ns = Counter(text_ns)
sorted_letters_ns = sorted(
    [(char, count, count / len(text_ns)) for char, count in letters_ns.items()],
    reverse=True, key=lambda x: x[1]
)

print("\nSorted letter frequency without spaces:")
print("(letter, count, frequency)")
for letter, count, frequency in sorted_letters_ns:
    print(letter, count, frequency)

bigrams_n_ns = defaultdict(int)
for i in range(0, len(text_ns) - 1, 2):
    bigrams_n_ns[text_ns[i:i+2]] += 1

bigrams_o_ns = defaultdict(int)
for i in range(len(text_ns) - 1):
    bigrams_o_ns[text_ns[i:i+2]] += 1

print("\nH1 (entropy of single letters without spaces):", calculate_entropy(letters_ns.values()))
print("H2 (entropy of bigrams without overlapping without spaces):", calculate_entropy(bigrams_n_ns.values()) / 2)
print("H2 (entropy of bigrams with overlapping without spaces):", calculate_entropy(bigrams_o_ns.values()) / 2)

unique_ns = sorted(letters_ns.keys())
total_n_ns = sum(bigrams_n_ns.values())
matrix_n_ns = pd.DataFrame(0.0, index=unique_ns, columns=unique_ns)
for bigram, freq in bigrams_n_ns.items():
    first_letter, second_letter = bigram[0], bigram[1]
    matrix_n_ns.at[first_letter, second_letter] = freq / total_n_ns

print("\nBigram frequency matrix without overlapping (no spaces):")
print(matrix_n_ns)
matrix_n_ns.to_csv('matrix_n_ns.csv', index=True)
time.sleep(2)

total_o_ns = sum(bigrams_o_ns.values())
matrix_o_ns = pd.DataFrame(0.0, index=unique_ns, columns=unique_ns)
for bigram, freq in bigrams_o_ns.items():
    first_letter, second_letter = bigram[0], bigram[1]
    matrix_o_ns.at[first_letter, second_letter] = freq / total_o_ns

print("\nBigram frequency matrix with overlapping (no spaces):")
print(matrix_o_ns)
matrix_o_ns.to_csv('matrix_o_ns.csv', index=True)

while True:
    input_letter = input('Enter a letter: ')
    if input_letter in unique_sp:
        possible_next_letters = matrix_o_sp.loc[input_letter]
        sorted_possible_letters = possible_next_letters[possible_next_letters > 0].sort_values(ascending=False)
        print(f"Possible letters after '{input_letter}': {', '.join(sorted_possible_letters.index)}")
    else:
        print("Letter not found in the text. Please enter a valid letter.")
