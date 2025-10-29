from collections import Counter

alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
m = len(alphabet)
russ_freq = {
    'о': 0.10983, 'е': 0.08483, 'а': 0.07998, 'и': 0.07367, 'н': 0.06700,
    'т': 0.06318, 'с': 0.05473, 'р': 0.04746, 'в': 0.04533, 'л': 0.04343,
    'к': 0.03486, 'м': 0.03203, 'д': 0.02977, 'п': 0.02804, 'у': 0.02615,
    'я': 0.02001, 'ы': 0.01898, 'ь': 0.01735, 'г': 0.01687, 'з': 0.01641,
    'б': 0.01592, 'ч': 0.01450, 'й': 0.01208, 'х': 0.00966, 'ж': 0.00940,
    'ш': 0.00718, 'ю': 0.00639, 'ц': 0.00486, 'щ': 0.00361, 'э': 0.00331,
    'ф': 0.00267, 'ъ': 0.00037
}

def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return ''.join(c for c in f.read().lower() if c in alphabet)
    except FileNotFoundError:
        print(f"файлу {filename} не знайдено")
        return None

def calculate_ic(text):
    n = len(text)
    if n <= 1:
        return 0
    freq = Counter(text)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

def expected_ic(freq_dict):
    return sum(p ** 2 for p in freq_dict.values())

expected_ic = expected_ic(russ_freq)
print(f"очікуваний IC = {expected_ic:.4f}\n")

def find_key_len(ciphertext, max_len=32, expected_ic=None):
    if expected_ic is None:
        expected_ic = 0.055
    
    ic_values = []
    for key_len in range(1, max_len + 1):
        groups = [ciphertext[i::key_len] for i in range(key_len)]
        avg_ic = sum(map(calculate_ic, groups)) / key_len
        ic_values.append((key_len, avg_ic))
    return ic_values, sorted(ic_values, key=lambda x: abs(x[1] - expected_ic))

def calculate_chi2(text, expected_freq): #критерій пірсона
    n = len(text)
    freq = Counter(text)
    return sum(
        (freq.get(ch, 0) - expected_freq.get(ch, 0.001) * n) ** 2 / (expected_freq.get(ch, 0.001) * n)
        for ch in alphabet
    )

def find_top_key_chars(group, top_n=5):
    candidates = []
    for shift in range(m):
        shifted = ''.join(alphabet[(alphabet.index(c) - shift) % m] for c in group)
        chi2 = calculate_chi2(shifted, russ_freq)
        candidates.append((alphabet[shift], chi2, shifted[:50]))
    return sorted(candidates, key=lambda x: x[1])[:top_n]

def analyze_key_positions(ciphertext, key_len, top_n=5):
    groups = [ciphertext[i::key_len] for i in range(key_len)]
    all_candidates = []

    for i, group in enumerate(groups):
        candidates = find_top_key_chars(group, top_n)
        all_candidates.append(candidates)
        top_chars = [c[0] for c in candidates[:3]]
        print(f"буква {i}: {top_chars}")

    return all_candidates

def decrypt_vigenere(ciphertext, key):
    key_indices = [alphabet.index(k) for k in key]
    return ''.join(
        alphabet[(alphabet.index(c) - key_indices[i % len(key)]) % m] if c in alphabet else c
        for i, c in enumerate(ciphertext)
    )

def test_key(ciphertext, key):
    print(f"\nавтоматично обраний ключ: {key}")
    decrypted = decrypt_vigenere(ciphertext, key)

    freq = Counter(decrypted)
    expected_top = ['о', 'е', 'а', 'и', 'н', 'т', 'с', 'р', 'в', 'л']
    most_common = freq.most_common(10)

    score = sum(ch in expected_top[:5] for ch, _ in most_common[:5])
    print(f"\nоцінка: {score}/5")
    if score >= 4:
        print("оціночно імовірно правильне дешифрування")
    elif score == 3:
        print("ну таке, не дуж")
    else:
        print("мабуть неправильне дешифрування")
    return decrypted

ciphertext = read_file('.txt')
if not ciphertext:
    exit()

ic_values, ic_sorted = find_key_len(ciphertext, max_len=20, expected_ic=None)
print("10 імовірних довжин ключа:")
for i, (k, ic) in enumerate(ic_sorted[:10], 1):
    print(f"{i:<3} | {k:<3} | IC={ic:.4f}")

best_key_len = ic_sorted[0][0]
print(f"\nнайкраща довжина ключа: {best_key_len}")

candidates = analyze_key_positions(ciphertext, best_key_len)
auto_key = ''.join(c[0][0] for c in candidates)
decrypted_text = test_key(ciphertext, auto_key)

with open('decrypted_text.txt', 'w', encoding='utf-8') as f:
    f.write(f"автоматично обраний ключ: {auto_key}\n{'-'*70}\n\n{decrypted_text}")
print("дешифрований текст збережено у файл 'decrypted_text.txt'")