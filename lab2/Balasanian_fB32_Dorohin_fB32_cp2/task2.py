import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from collections import Counter

alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
m = len(alphabet)

freqs = {
    'о':0.1085,'и':0.0918,'е':0.0888,'а':0.0746,'с':0.0575,'т':0.0573,'н':0.0555,
    'в':0.0508,'л':0.0443,'р':0.0430,'д':0.0357,'м':0.0331,'п':0.0271,'к':0.0265,
    'у':0.0259,'г':0.0221,'я':0.0204,'ы':0.0192,'б':0.0186,'з':0.0163,'ь':0.0151,
    'х':0.0115,'ч':0.0106,'й':0.0094,'ж':0.0089,'ш':0.0075,'ю':0.0070,'ц':0.0055,
    'щ':0.0036,'ф':0.0024,'э':0.0010,'ъ':0.0005
}

def prepare_text(text):
    text = text.lower()
    return "".join([c for c in text if c in alphabet])

def index_coincidence(text):
    n = len(text)
    freqs_text = Counter(text)
    return sum(f*(f-1) for f in freqs_text.values()) / (n*(n-1)) if n>1 else 0

def split_blocks(text, key_len):
    blocks = ['' for _ in range(key_len)]
    for i, c in enumerate(text):
        blocks[i % key_len] += c
    return blocks

def best_shift(block):
    n = len(block)
    if n == 0:
        return 0
    idxs = [alphabet.index(c) for c in block]
    best_s, max_corr = 0, -1
    for s in range(m):
        counts = [0]*m
        for x in idxs:
            y = (x - s) % m
            counts[y] += 1
        corr = sum((counts[i]/n) * freqs[alphabet[i]] for i in range(m))
        if corr > max_corr:
            max_corr = corr
            best_s = s
    return best_s

def decrypt_vigenere(shifr, key):
    key_index = [alphabet.index(c) for c in key]
    key_len = len(key)
    result = []
    for i, c in enumerate(shifr):
        c_idx = alphabet.index(c)
        p_idx = (c_idx - key_index[i % key_len]) % m
        result.append(alphabet[p_idx])
    return ''.join(result)

with open("cipher.txt", "r", encoding="utf-8") as f:
    shifr = prepare_text(f.read())

print(f"Довжина очищеного шифротексту: {len(shifr)}")
print("Перші 200 символів:", shifr[:200])

target_ic = 0.0569
best_r, best_diff = 2, 1e9
r_values, avg_ic_values = [], []

print("\nr\tІндекс відповідності")
print("-"*25)
for r in range(2, 31):
    blocks = split_blocks(shifr, r)
    avg_ic = sum(index_coincidence(b) for b in blocks)/r
    diff = abs(avg_ic - target_ic)
    if diff < best_diff:
        best_diff = diff
        best_r = r
    print(f"{r}\t{avg_ic:.5f}")
    r_values.append(r)
    avg_ic_values.append(avg_ic)

print(f"\nЙмовірна довжина ключа: {best_r}")

blocks = split_blocks(shifr, best_r)
key = ''.join(alphabet[best_shift(b)] for b in blocks)
print("Відновлений ключ:", key)

plain_text = decrypt_vigenere(shifr, key)
with open("decrypted.txt", "w", encoding="utf-8") as f:
    f.write(f"Відновлений ключ: {key}\n\n")
    f.write(plain_text)

plt.figure(figsize=(10,5))
plt.bar(r_values, avg_ic_values, color='skyblue')
plt.axhline(y=target_ic, color='r', linestyle='--', label='Теоретичне IC мови')
plt.xlabel("Довжина ключа r")
plt.ylabel("Середній індекс відповідності")
plt.title("Середній IC для різних довжин ключа")
plt.legend()
plt.tight_layout()
plt.savefig("ic_r_plot.png")
plt.show()
