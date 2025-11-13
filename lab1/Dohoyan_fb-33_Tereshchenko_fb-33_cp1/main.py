import re, math, os
from collections import Counter
import pandas as pd

def normalize(text, keep_spaces=True):
    text = text.lower().replace('ё','е').replace('ъ','ь')
    if keep_spaces:
        text = re.sub(r'[^а-я ]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
    else:
        text = re.sub(r'[^а-я]', '', text)
    return text


def frequencies(seq, n=1, step=1):
    items = [seq[i:i+n] for i in range(0, len(seq)-n+1, step)]
    cnt = Counter(items)
    total = sum(cnt.values())
    return {k: v/total for k,v in cnt.items()}

def bigram_matrix(bigrams):
    abc = list("абвгдежзийклмнопрстуфхцчшщыьэюяёъ ")
    m = pd.DataFrame(0.0, index=abc, columns=abc)
    for bg, f in bigrams.items():
        if len(bg) == 2: m.at[bg[0], bg[1]] = round(f,6)
    return m

def entropy(freqs): return -sum(p*math.log2(p) for p in freqs.values())

def process(path, keep_spaces=True):
    with open(path, encoding="utf-8") as f: text = normalize(f.read(), keep_spaces)
    chars = frequencies(text)
    bigr_1, bigr_2 = frequencies(text,2,1), frequencies(text,2,2)

    out = f"results_{'spaces' if keep_spaces else 'nospace'}.xlsx"
    if os.path.exists(out): os.remove(out)
    with pd.ExcelWriter(out) as w:
        pd.DataFrame(chars.items(), columns=["Символ","Частота"]).to_excel(w, "Частоти", index=False)
        bigram_matrix(bigr_1).to_excel(w, "Біграми з перекриттям")
        bigram_matrix(bigr_2).to_excel(w, "Біграми без перекриття")

    print(f"{'З пробілами' if keep_spaces else 'Без пробілів'}:")
    print(f"H1 = {entropy(chars):.6f}")
    print(f"H2 перекриття = {entropy(bigr_1)/2:.6f}")
    print(f"H2 без перекриття = {entropy(bigr_2)/2:.6f}\n")

file = "kafka.txt"
process(file, keep_spaces=True)
process(file, keep_spaces=False)
