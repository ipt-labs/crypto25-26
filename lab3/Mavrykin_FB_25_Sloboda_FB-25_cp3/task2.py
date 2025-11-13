def calc(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
    count = {}
    total = 0

    for i in range(0, len(text) - 1):
        bi = text[i:i+2]
        if len(bi) == 2:
            if bi in count:
                count[bi] += 1
            else:
                count[bi] = 1
            total += 1

    freq = {bi: cnt / total for bi, cnt in count.items()}
    top5 = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
    return freq, top5

filename = '02.txt'
freq, top5 = calc(filename)

print("Частоти 5 найпоширеніших біграм:")
for bigram, f in top5:
    print(f"'{bigram}': {f:.2%}")
