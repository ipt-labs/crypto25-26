import collections, math
import matplotlib.pyplot as plt

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
M = 32
MAX_R_TO_CHECK = 30
RUSSIAN_FREQS = {'о': 0.1097, 'е': 0.0845}

CHAR_TO_INT = {c: i for i, c in enumerate(ALPHABET)}
INT_TO_CHAR = {i: c for i, c in enumerate(ALPHABET)}

def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            t = f.read().lower()
            t = "".join(c for c in t if c in CHAR_TO_INT)
            print(f"[Успіх] Зчитано {len(t)} символів")
            return t
    except:
        print("Файл не знайдено або недоступний")
        return ""

def find_key_length(ciphertext):
    print("\nВизначення довжини ключа методом збігів")
    n = len(ciphertext)
    res = []
    r_values = []
    matches = []

    for r in range(2, MAX_R_TO_CHECK + 1):
        dr = sum(1 for i in range(n - r) if ciphertext[i] == ciphertext[i + r])
        res.append((r, dr))
        r_values.append(r)
        matches.append(dr)
        print(f"  r={r}: збігів={dr}")

    plt.figure(figsize=(10, 5))
    plt.plot(r_values, matches, marker='o')
    plt.title("Кількість збігів в залежності від r")
    plt.xlabel("r (потенційна довжина ключа)")
    plt.ylabel("Кількість збігів")
    plt.grid(True)
    plt.show()

    res.sort(key=lambda x: x[1], reverse=True)
    likely = res[0][0]
    print(f"Найімовірна довжина ключа: r = {likely}\n")
    return likely

def calculate_chi2(text):
    cnt = collections.Counter(text)
    L = len(text)
    if L == 0: return math.inf
    s = 0
    for c in ALPHABET:
        o = cnt.get(c, 0)
        e = RUSSIAN_FREQS.get(c, 0.00001) * L
        d = o - e
        s += (d * d) / e
    return s

def find_key_advanced(ciphertext, r):
    print("Пошук ключа частотним аналізом")
    key = ""
    for i in range(r):
        block = ciphertext[i::r]
        best = None
        best_chi = math.inf
        print(f"\n  Аналіз позиції {i+1}/{r}, блок довжини {len(block)}")
        for g in range(M):
            dec = "".join(INT_TO_CHAR[(CHAR_TO_INT[c] - g) % M] for c in block)
            chi = calculate_chi2(dec)
            if chi < best_chi:
                best_chi = chi
                best = INT_TO_CHAR[g]
        print(f"  Найкраща літера: '{best}' (chi²={best_chi:.2f})")
        key += best
    print(f"\nЗнайдений ключ: {key}\n")
    return key

def decrypt_vigenere(ciphertext, key):
    res = ""
    r = len(key)
    for i, c in enumerate(ciphertext):
        try:
            x = (CHAR_TO_INT[c] - CHAR_TO_INT[key[i % r]]) % M
            res += INT_TO_CHAR[x]
        except:
            res += '?'
    return res

def main():
    filename = "encrypted_13.txt"
    text = read_file(filename)
    if not text:
        print("Немає даних для обробки.")
        return

    r = find_key_length(text)
    key = find_key_advanced(text, r)
    decrypted = decrypt_vigenere(text, key)

    print("\nРОЗШИФРОВАНИЙ ТЕКСТ")
    print(decrypted[:2000])
    if len(decrypted) > 2000:
        print("...скорочено...")

    output_file = "decrypted.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(decrypted)

if __name__ == "__main__":
    main()