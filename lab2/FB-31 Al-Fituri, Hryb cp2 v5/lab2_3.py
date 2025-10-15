
# 3. Використовуючи наведені теоретичні відомості, розшифрувати наданий шифртекст (згідно свого номеру варіанта). 
import random
import time
from collections import Counter

random.seed(42)

# Алфавіт
alphabet = list("абвгдежзийклмнопрстуфхцчшщъыьэюя")
m = len(alphabet)
map_idx = {c: i for i, c in enumerate(alphabet)}

# Найуживаніші російські слова
common_words = [
    "и", "в", "на", "не", "что", "как", "это", "по", "за", "с", "для",
    "он", "она", "они", "его", "ее", "так", "же", "котор", "быть",
    "есть", "только", "уже", "чтобы", "если"
]

# Зчитування файлу
with open("cipher.txt", encoding="utf-8") as f:
    raw = f.read().lower().replace("ё", "е")
text = "".join(ch for ch in raw if ch in map_idx)

N = len(text)
print("Довжина очищеного тексту:", N)
if N == 0:
    raise SystemExit("cipher.txt порожній або не містить допустимих букв з алфавіту.")

# Функції
def index_of_coincidence(s):
    if len(s) <= 1:
        return 0.0
    freqs = Counter(s)
    n = len(s)
    return sum(v * (v - 1) for v in freqs.values()) / (n * (n - 1))

def compute_dr(s, maxr=30):
    n = len(s)
    return [(r, sum(1 for i in range(n - r) if s[i] == s[i + r])) for r in range(1, maxr + 1)]

def decrypt_with_shifts(s, shifts):
    L = len(shifts)
    out_chars = []
    for i, ch in enumerate(s):
        a = map_idx[ch]
        k = shifts[i % L]
        out_chars.append(alphabet[(a - k) % m])
    return "".join(out_chars)

russian_freq = {
    'о': 0.1097, 'е': 0.0845, 'а': 0.0801, 'и': 0.0735, 'н': 0.0670, 'т': 0.0632,
    'с': 0.0547, 'р': 0.0473, 'в': 0.0454, 'л': 0.0434, 'к': 0.0349, 'м': 0.0321,
    'д': 0.0298, 'п': 0.0281, 'у': 0.0262, 'я': 0.0201, 'ы': 0.0189, 'ь': 0.0174,
    'г': 0.0169, 'з': 0.0165, 'б': 0.0159, 'ч': 0.0144, 'й': 0.0121, 'х': 0.0097,
    'ж': 0.0094, 'ш': 0.0073, 'ю': 0.0064, 'ц': 0.0048, 'щ': 0.0036, 'э': 0.0032,
    'ъ': 0.0004
}
r_freq = [russian_freq.get(c, 0.0) for c in alphabet]

def find_shifts_chi(s, L):
    shifts = []
    for i in range(L):
        block = s[i::L]
        if not block:
            shifts.append(0)
            continue
        counts = [block.count(c) for c in alphabet]
        total = len(block)
        best_k = 0
        best_score = -1e9
        for k in range(m):
            score = 0.0
            for j in range(m):
                expected = r_freq[(j - k) % m]
                score += (counts[j] / total) * expected
            if score > best_score:
                best_score = score
                best_k = k
        shifts.append(best_k)
    return shifts

def score_text_words_ioc(sample_text):
    s = sample_text[:3000] if len(sample_text) > 3000 else sample_text
    score = 0.0
    for w in common_words:
        cnt = s.count(w)
        if cnt:
            score += cnt * (len(w) + 2)
    score += index_of_coincidence(s) * 50.0
    return score

def improve_key(s, init_shifts, iterations=800, restarts=5):
    best_shifts = init_shifts[:]
    best_plain = decrypt_with_shifts(s, best_shifts)
    best_score = score_text_words_ioc(best_plain)

    for r in range(restarts):
        if r == 0:
            cur = init_shifts[:]
        else:
            cur = [(k + random.randint(-2, 2)) % m for k in init_shifts]

        cur_plain = decrypt_with_shifts(s, cur)
        cur_score = score_text_words_ioc(cur_plain)
        T0 = 1.0

        for it in range(iterations):
            i = random.randrange(len(cur))
            step = random.choice([-3, -2, -1, 1, 2, 3])
            old = cur[i]
            cur[i] = (cur[i] + step) % m

            cand_plain = decrypt_with_shifts(s, cur)
            cand_score = score_text_words_ioc(cand_plain)
            T = T0 * (1 - it / iterations)

            if cand_score > cur_score or random.random() < 0.001 + 0.3 * T:
                cur_score = cand_score
                cur_plain = cand_plain
                if cur_score > best_score:
                    best_score = cur_score
                    best_shifts = cur[:]
                    best_plain = cur_plain
            else:
                cur[i] = old

        print(f"Перезапуск {r + 1}/{restarts} — поточний найкращий score={best_score:.2f}")

    return best_shifts, best_plain, best_score

print("Обчислення IoC для L=1..30")
IoC_list = []
for L in range(1, 31):
    blocks = [text[i::L] for i in range(L)]
    avg_ioc = sum(index_of_coincidence(b) for b in blocks) / L
    IoC_list.append((L, avg_ioc))
    print(f"L={L:2d}, IoC={avg_ioc:.5f}")

dr = compute_dr(text, maxr=30)
print("\nD_r (r=1..30):")
for r, cnt in dr:
    print(f"r={r:2d}, D_r={cnt}")

import matplotlib.pyplot as plt

# Графік IoC 
L_values, IoC_values = zip(*IoC_list)
plt.figure(figsize=(10, 5))
plt.plot(L_values, IoC_values, marker='o')
plt.title("Залежність IoC від довжини L")
plt.xlabel("L (довжина підрядка)")
plt.ylabel("Index of Coincidence (IoC)")
plt.grid(True)
plt.xticks(range(1, 31))
plt.savefig("IoC_plot.png", dpi=300)
plt.close()

# Графік D_r
r_values, D_values = zip(*dr)
plt.figure(figsize=(10, 5))
plt.bar(r_values, D_values, color='skyblue')
plt.title("Кількість збігів D_r для r=1..30")
plt.xlabel("r (відстань між символами)")
plt.ylabel("D_r (кількість збігів)")
plt.grid(axis='y')
plt.xticks(range(1, 31))
plt.savefig("Dr_plot.png", dpi=300)
plt.close()

print("Графіки IoC та D_r збережено як IoC_plot.png та Dr_plot.png")

top_L = [L for L, _ in sorted(IoC_list, key=lambda x: x[1], reverse=True)[:6]]
print("\nЙмовірні довжини ключа:", top_L)

overall_best = (None, None, -1.0, None)

for L in top_L:
    print(f"\nПеревірка L={L}")
    init = find_shifts_chi(text, L)
    key_letters_init = ''.join(alphabet[k] for k in init)
    plain_init = decrypt_with_shifts(text, init)
    s_init = score_text_words_ioc(plain_init)
    print("Початковий ключ:", key_letters_init, "оцінка:", round(s_init, 2))

    start = time.time()
    best_shifts, best_plain, best_score = improve_key(text, init, iterations=800, restarts=5)
    elapsed = time.time() - start
    key_letters_best = ''.join(alphabet[k] for k in best_shifts)
    print(f"Отримано ключ: {key_letters_best} (довжина {L}) оцінка={round(best_score, 2)} час={elapsed:.1f}s")
    print("Фрагмент розшифровки (перші 600 символів):")
    print(best_plain[:600])

    if best_score > overall_best[2]:
        overall_best = (L, key_letters_best, best_score, best_plain)

if overall_best[0] is not None:
    L, key_text, s, plain = overall_best
    print("\nПІДСУМКОВИЙ РЕЗУЛЬТАТ")
    print(f"Оптимальна довжина ключа: {L}")
    print(f"Ключ Віженера: {key_text}")
    print(f"Оцінка: {round(s, 2)}")
    print("Фрагмент розшифрованого тексту:")
    print(plain[:2000])

    output_path = "result_lab2_3.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("ПІДСУМКОВІ РЕЗУЛЬТАТИ\n\n")
        f.write(f"Оптимальна довжина ключа: {L}\n")
        f.write(f"Ключ Віженера: {key_text}\n\n")
        f.write("Фрагмент розшифрованого тексту:\n")
        f.write(plain[:2000])
        f.write("\n\nПовний розшифрований текст:\n")
        f.write(plain)

    print(f"Результат і ключ збережено у файл {output_path}")
else:
    print("Не вдалося знайти осмислену розшифровку.")