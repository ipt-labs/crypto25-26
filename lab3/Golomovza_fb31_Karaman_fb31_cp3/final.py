from collections import Counter
import sys
sys.stdout.reconfigure(encoding='utf-8')


# -----------------------------
# 1. Алфавіт та параметри
# -----------------------------
alphabet = "абвгдежзийклмнопрстуфхцчшщьыэюя"  # без ё, з ъ
alen = len(alphabet)
m = alen * alen

# -----------------------------
# 2. Зчитування та очищення тексту
# -----------------------------
with open("07.txt", "r", encoding="cp1251") as f:
    encoded_text = f.read().lower()

# очищаємо від усього, чого немає в алфавіті
encoded_text = ''.join(ch for ch in encoded_text if ch in alphabet)

# -----------------------------
# 3. Допоміжні функції
# -----------------------------
def egcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y

def modinv(a, mod):
    g, x, y = egcd(a, mod)
    if g != 1:
        return None
    return x % mod

def solve_linear(a, b, mod):
    """Розв'язує a*x ≡ b (mod m), повертає список можливих x"""
    g, _, _ = egcd(a, mod)
    if b % g != 0:
        return []
    a1, b1, m1 = a // g, b // g, mod // g
    inv_a1 = modinv(a1, m1)
    if inv_a1 is None:
        return []
    x0 = (inv_a1 * b1) % m1
    return [(x0 + i * m1) % mod for i in range(g)]

def bigr_to_num(bigr):
    """перетворює біграму у число"""
    return alphabet.index(bigr[0]) * alen + alphabet.index(bigr[1])

def num_to_bigr(num):
    """перетворює число у біграму"""
    return alphabet[num // alen] + alphabet[num % alen]

def decode(text, a, b):
    """розшифровує текст при даних a, b"""
    inv_a = modinv(a, m)
    if inv_a is None:
        return ""
    res = []
    for i in range(0, len(text) - 1, 2):
        bg = text[i:i+2]
        if len(bg) < 2:
            continue
        y = bigr_to_num(bg)
        x = (inv_a * (y - b)) % m
        res.append(num_to_bigr(x))
    return "".join(res)

# -----------------------------
# 4. Частоти біграм
# -----------------------------
def bigram_freq(text):
    pairs = [text[i:i+2] for i in range(0, len(text)-1, 2)]
    c = Counter(pairs)
    return c.most_common()

# -----------------------------
# 5. Основна логіка підбору ключа
# -----------------------------
top_plain = ["ст", "но", "то", "на", "ен"]
freq_cipher = bigram_freq(encoded_text)
top_cipher = [bg for bg, _ in freq_cipher[:5]]

print("ТОП-5 біграм шифртексту:", top_cipher)
print()

best_score = -1e9
best_text = ""
best_a, best_b = 0, 0

all_keys = []  # список для збереження всіх ключів

def score_text(txt):
    """Оцінює якість розшифровки (чим вище, тим краще)"""
    vowels = "аеёиоуыэюя"
    if not txt:
        return -1e9
    freq = Counter(txt)
    v_ratio = sum(freq[ch] for ch in vowels) / len(txt)
    score = 0
    score -= abs(v_ratio - 0.45) * 100  # середній відсоток голосних
    score -= txt.count("ьь") * 100
    score -= txt.count("ыь") * 100
    score += sum(freq[ch] for ch in "еаотинсрл") / len(txt) * 300
    return score

# -----------------------------
# 6. Перебір співставлень біграм
# -----------------------------
print("=== СПІВСТАВЛЕННЯ БІГРАМ ТА ПОШУК КЛЮЧІВ ===\n")

display_limit = 10  # скільки співставлень показати у консолі
shown = 0

for X1 in top_plain:
    for X2 in top_plain:
        if X1 == X2:
            continue
        x1, x2 = bigr_to_num(X1), bigr_to_num(X2)
        for Y1 in top_cipher:
            for Y2 in top_cipher:
                if Y1 == Y2:
                    continue
                y1, y2 = bigr_to_num(Y1), bigr_to_num(Y2)

                # вивід лише перших 10 співставлень
                if shown < display_limit:
                    print(f"[{shown+1}] Мова: ({X1}, {X2}) ↔ Шифртекст: ({Y1}, {Y2})")
                    shown += 1

                sols = solve_linear((x1 - x2) % m, (y1 - y2) % m, m)
                for a in sols:
                    b = (y1 - a * x1) % m
                    dec = decode(encoded_text, a, b)
                    sc = score_text(dec)
                    all_keys.append((a, b, sc, X1, X2, Y1, Y2))
                    if sc > best_score:
                        best_score = sc
                        best_text = dec
                        best_a, best_b = a, b

print("\n=== ПІДБІР ЗАВЕРШЕНО ===\n")

# -----------------------------
# 7. Результати
# -----------------------------
print(f"[НАЙКРАЩИЙ КЛЮЧ]: a = {best_a}, b = {best_b}, score = {best_score:.2f}")
print("\n--- РОЗШИФРОВАНИЙ ТЕКСТ (перші 300 символів) ---\n")
print(best_text[:300])

# зберігаємо розшифрований текст
with open("decrypt.txt", "w", encoding="utf-8") as f:
    f.write(best_text)
print("\n Повний текст збережено у decrypt.txt")

# зберігаємо всі ключі у файл
with open("all_keys.txt", "w", encoding="utf-8") as f:
    for a, b, sc, X1, X2, Y1, Y2 in all_keys:
        f.write(f"{X1},{X2} ↔ {Y1},{Y2} | a={a}, b={b}, score={sc:.4f}\n")

print(" Усі ключі та співставлення збережено у all_keys.txt")
