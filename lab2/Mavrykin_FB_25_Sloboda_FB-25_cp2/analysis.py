from collections import Counter
import matplotlib.pyplot as plt

alh = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def ic(text):
    n = len(text)
    if n <= 1:
        return 0
    freq = Counter(text)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

def method1(text, max_r=30):
    results = {}
    for r in range(2, max_r + 1):
        blocks = ['' for _ in range(r)]
        for i, char in enumerate(text):
            blocks[i % r] += char
        iocs = [ic(block) for block in blocks]
        avg = sum(iocs) / r
        results[r] = avg
        print(f"r: {r}, IC: {avg:.6f}")

    plt.figure(figsize=(12, 6))
    plt.plot(list(results.keys()), list(results.values()), 'b-o')
    plt.xlabel("r")
    plt.ylabel("IC")
    plt.title("Method 1")
    plt.grid()
    plt.show()
    return results

def method2(text, max_r=30):
    results = {}
    n = len(text)
    for r in range(2, max_r + 1):
        count = 0
        for i in range(n - r):
            if text[i] == text[i + r]:
                count += 1
        results[r] = count

    plt.figure(figsize=(12, 6))
    plt.plot(list(results.keys()), list(results.values()), 'r-o')
    plt.xlabel("r")
    plt.ylabel("D(r)")
    plt.title("Method 2")
    plt.grid()
    plt.show()
    return results

def find_key(text, r):
    blocks = []
    for i in range(r):
        b = text[i::r]
        blocks.append(b)

    key = ''
    for b in blocks:
        freq = {}
        for ltr in b:
            if ltr in freq:
                freq[ltr] += 1
            else:
                freq[ltr] = 1
        freq_sorted = dict(sorted(freq.items(), key=lambda item: item[1], reverse=True))
        most = list(freq_sorted.keys())[0]
        k_ind = (alh.index(most) - alh.index('о')) % 32
        key += alh[k_ind]
    return key
