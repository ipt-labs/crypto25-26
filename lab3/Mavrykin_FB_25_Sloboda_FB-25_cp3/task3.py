def gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y

def inverse(a, m):
    g, x, _ = gcd(a, m)
    if g != 1:
        return None
    return x % m

def solve(a, b, m):
    g, x, y = gcd(a, m)
    if b % g != 0:
        return []
    a1 = a // g
    b1 = b // g
    m1 = m // g

    inv = inverse(a1, m1)
    if inv is None:
        return []

    x0 = (inv * b1) % m1
    result = []
    for i in range(g):
        result.append(x0 + i * m1)
    return result

ct_bis = ['йа', 'юа', 'чш', 'рп', 'юд']
tv_bis = ['ст', 'но', 'то', 'на', 'ен']

print("5 найчастіших біграм шифртексту:", ct_bis)
print("5 найчастіших біграм російської мови:", tv_bis)
alph = 'абвгдежзийклмнопрстуфхцчшщьыэюя'
ct_num = {ch: i for i, ch in enumerate(alph)}
num_ct = {i: ch for i, ch in enumerate(alph)}
m2 = 961

pairs = [(tv_bi, ct_bi) for tv_bi in tv_bis for ct_bi in ct_bis]

n_pairs = [(31 * ct_num[pair[0][0]] + ct_num[pair[0][1]],
            31 * ct_num[pair[1][0]] + ct_num[pair[1][1]]) for pair in pairs]

keys = []

for i in range(len(n_pairs)):
    x1, y1 = n_pairs[i]
    for j in range(i + 1, len(n_pairs)):
        x2, y2 = n_pairs[j]
        diff_x = x1 - x2
        diff_y = y1 - y2

        if diff_x == 0:
            continue

        answer = solve(diff_x, diff_y, m2)
        if answer:
            for x in answer:
                a = x
                b = (y1 - a * x1) % m2
                keys.append((a, b))

print(f"\nКількість кандидатів: {len(keys)}")
print("\nКандидати (a, b):")
for key in keys:
    print(key)

with open('02.txt', 'r', encoding='utf-8') as f:
    text = f.read().replace('\n', '')
nums = [ct_num[ch] for ch in text]

def decrypt(nums, a, b, m):
    m2 = m ** 2
    vt = []

    a_inv = inverse(a, m2)

    if a_inv is None:
        return None

    for i in range(0, len(nums), 2):
        y = nums[i]
        if i < len(nums) - 1:
            n_y = nums[i + 1]
        else:
            n_y = 0

        idx = y * 31 + n_y
        x = (a_inv * (idx - b)) % m2
        x1, x2 = (x // 31), (x % 31)

        vt.append(num_ct[x1 % m])
        vt.append(num_ct[x2 % m])

    return ''.join(vt)

full_vt = {}
for a, b in keys:
    decr = decrypt(nums, a, b, len(alph))
    if decr:
        full_vt[(a, b)] = decr

rare_bis = ["мэ", "хэ", "бц", "оэ", "фм", "вщ", "иэ", "бб", "эм", "бт",
            "фк", "ыя", "ыц", "дщ", "нж", "лщ", "эг", "уу", "фс", "ыя"]

def get_bigrams(text):
    return [text[i:i+2] for i in range(0, len(text), 2)]

def count_rare(text, rare_bis):
    bi = get_bigrams(text)
    return sum(1 for b in bi if b in rare_bis)

bis_freq = {}
for key, vt in full_vt.items():
    freq_rare = count_rare(vt, rare_bis)
    bis_freq[key] = freq_rare

sorted_keys = sorted(bis_freq.items(), key=lambda x: x[1])

print("\nКлючі з найменшою кількістю рідкісних біграм:")
for i, (key, freq_rare) in enumerate(sorted_keys[:10]):
    print(f"{i+1}. Ключ {key} - Кількість рідкісних біграм: {freq_rare}")

best_key = sorted_keys[0][0]
print(f"\nОбраний ключ: {best_key}")
print(f"\nРозшифрований текст:\n{full_vt[best_key]}")
