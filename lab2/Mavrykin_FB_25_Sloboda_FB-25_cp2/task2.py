from analysis import ic
import matplotlib.pyplot as plt

with open('sample_cleaned.txt', 'r', encoding='utf8') as f:
    open_text = f.read()

open_ic = ic(open_text)
print(f'Open text IC: {open_ic:.6f}')
print()

results = {'Open text': open_ic}

key_lengths = [2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

for r in key_lengths:
    filename = f'cipher-{r}.txt'
    try:
        with open(filename, 'r', encoding='utf8') as f:
            cipher = f.read()
        cipher_ic = ic(cipher)
        results[f'r={r}'] = cipher_ic
        print(f'r={r}: {cipher_ic:.6f}')
    except:
        pass

plt.figure(figsize=(14, 6))
labels = list(results.keys())
values = list(results.values())
colors = ['green'] + ['blue'] * (len(values) - 1)
plt.bar(labels, values, color=colors)
plt.xlabel('Text')
plt.ylabel('IC')
plt.title('IC comparison')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.show()
