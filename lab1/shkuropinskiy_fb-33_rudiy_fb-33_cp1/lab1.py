import pandas as pd
import math

russian = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

def count_letters(text):
    dictionary = {}

    for char in text:
        if char in russian:
            if char in dictionary:
                dictionary[char] += 1
            else:
                dictionary[char] = 1

    return dictionary

def count_for_leters(result_letters):
    frequencies = []
    total_letters = sum(result_letters.values())
    entropy = 0

    for letter, count in result_letters.items():
        frequency = count / total_letters
        frequencies.append((letter, frequency))
        entropy -= frequency * math.log(frequency, 2)

    frequencies.sort(key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(frequencies, columns=["letter", "frequency"])

    df.to_excel("letters.xlsx", index=False)

    H1_max = math.log2(len(russian))
    R1 = 1 - (entropy / H1_max)

    print(f"Nadlishkovist {R1}")
    print(f"Entropy letters: {entropy}")
def bigrams(text, letter_russian,  filename="bigrams.xlsx", step=1):
    bigrams_count = {}
    entropy = 0

    for i in range(0, len(text) - 1, step):
        a, b = text[i], text[i + 1]
        bigram = a + b
        if bigram in bigrams_count:
            bigrams_count[bigram] += 1
        else:
            bigrams_count[bigram] = 1
        
    total_bigrams = sum(bigrams_count.values())
    df = pd.DataFrame(0, index=list(letter_russian), columns=list(letter_russian), dtype=float)
    for bigram, count in bigrams_count.items():
        a, b = bigram[0], bigram[1]
        df.loc[a, b] = count / total_bigrams
        frequency = count / total_bigrams
        entropy -= 0.5 * frequency * math.log(frequency, 2)

    df.to_excel(filename)

    H2_max = math.log2(len(letter_russian))
    R2 = 1 - entropy / H2_max

    print(f"Nadlishkovist bigrams: {R2}")
    print(f"Entropy bigrams: {entropy}")


if __name__ == "__main__":

    with open("merged_without_spaces.txt", "r", encoding="utf-8") as file:
        text = file.read()

    result_letters = count_letters(text)

    count_for_leters(result_letters)
    bigrams(text, russian, step=1, filename="bigrams_pereten.xlsx")
    bigrams(text, russian, step=2, filename="bigrams_no_pereten.xlsx")

