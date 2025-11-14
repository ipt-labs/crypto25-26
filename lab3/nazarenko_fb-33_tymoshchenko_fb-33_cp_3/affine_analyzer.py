import csv
from collections import Counter

ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
M = len(ALPHABET)
MOD = M * M
RUSSIAN_TOP5 = ["ст", "но", "то", "на", "ен"]
FORBIDDEN = {"аь", "оь", "уь", "ыь", "эь", "жы", "шы", "ыы", "йй", "ьь"}
FREQUENT = {"о", "е", "а", "и", "н", "т", "с"}
RARE = {"ф", "щ", "ь", "ы", "э"}

char2num = {ch: i for i, ch in enumerate(ALPHABET)}
num2char = {i: ch for i, ch in enumerate(ALPHABET)}


def extended_gcd(a, b):
    #Розширений алгоритм Евкліда
    if b == 0:
        return (a, 1, 0)
    r_prev, r_curr = a, b
    u_prev, u_curr = 1, 0
    v_prev, v_curr = 0, 1
    while r_curr != 0:
        q = r_prev // r_curr
        r_prev, r_curr = r_curr, r_prev - q * r_curr
        u_prev, u_curr = u_curr, u_prev - q * u_curr
        v_prev, v_curr = v_curr, v_prev - q * v_curr
    return (r_prev, u_prev, v_prev)


def mod_inverse(a, mod):
    #Обернений елемент за модулем
    gcd, u, _ = extended_gcd(a, mod)
    return u % mod if gcd == 1 else None


def solve_congruence(a, b, mod):
    #Розв'язування лінійного порівняння ax = b (mod n)
    a, b = a % mod, b % mod
    gcd, _, _ = extended_gcd(a, mod)
    if b % gcd != 0:
        return []
    a1, b1, mod1 = a // gcd, b // gcd, mod // gcd
    inv = mod_inverse(a1, mod1)
    if inv is None:
        return []
    x0 = (inv * b1) % mod1
    return [(x0 + k * mod1) % mod for k in range(gcd)]


def normalize(text):
    #Нормалізація тексту
    text = text.lower().replace("ё", "е").replace("ъ", "ь")
    return "".join(ch for ch in text if ch in ALPHABET)


def bigram_to_num(bg):
    #Перетворення біграми в число
    return char2num[bg[0]] * M + char2num[bg[1]]


def num_to_bigram(n):
    #Перетворення числа в біграму
    return num2char[n // M] + num2char[n % M]


def split_bigrams(text):
    #Розбиття тексту на біграми
    return [text[i:i+2] for i in range(0, len(text)-1, 2)]


def decrypt(text, a, b):
    #Розшифрування тексту
    inv_a = mod_inverse(a, MOD)
    if inv_a is None:
        return None
    result = []
    for bg in split_bigrams(text):
        Y = bigram_to_num(bg)
        X = (inv_a * (Y - b)) % MOD
        result.append(num_to_bigram(X))
    return "".join(result)


def score_text(text):
    #Оцінка якості тексту
    if len(text) < 10:
        return -1000
    
    freq = Counter(text)
    n = len(text)
    score = 0
    
    # Часті літери повинні складати 40-50%
    freq_sum = sum(freq.get(ch, 0) for ch in FREQUENT) / n
    score += freq_sum * 100
    
    # Рідкісні літери повинні бути малими
    rare_sum = sum(freq.get(ch, 0) for ch in RARE) / n
    if rare_sum > 0.15:
        score -= (rare_sum - 0.15) * 200
    
    # Заборонені біграми
    overlapping = [text[i:i+2] for i in range(len(text)-1)]
    forbidden_count = sum(1 for bg in overlapping if bg in FORBIDDEN)
    score -= (forbidden_count / len(overlapping)) * 500
    
    # Індекс відповідності
    counter = Counter(text)
    ic = sum(c * (c - 1) for c in counter.values()) / (n * (n - 1))
    score -= abs(ic - 0.055) * 1000
    
    return score


def generate_candidates(cipher_top5):
    #Генерація кандидатів на ключ
    candidates = set()
    
    for Y1_str in cipher_top5:
        for Y2_str in cipher_top5:
            if Y1_str == Y2_str:
                continue
            Y1, Y2 = bigram_to_num(Y1_str), bigram_to_num(Y2_str)
            
            for X1_str in RUSSIAN_TOP5:
                for X2_str in RUSSIAN_TOP5:
                    if X1_str == X2_str:
                        continue
                    X1, X2 = bigram_to_num(X1_str), bigram_to_num(X2_str)
                    
                    delta_X = (X1 - X2) % MOD
                    delta_Y = (Y1 - Y2) % MOD
                    
                    for a in solve_congruence(delta_X, delta_Y, MOD):
                        gcd, _, _ = extended_gcd(a, MOD)
                        if gcd == 1:
                            b = (Y1 - a * X1) % MOD
                            candidates.add((a, b))
    
    return sorted(list(candidates))


def analyze(input_file):
    #Головна функція криптоаналізу
    print("КРИПТОАНАЛІЗ АФІННОЇ БІГРАМНОЇ ПІДСТАНОВКИ")
    
    # Читання файлу
    with open(input_file, "r", encoding="utf-8") as f:
        cipher = f.read()
    
    # Крок 1: Нормалізація
    norm = normalize(cipher)
    print(f"\n[Крок 1] Нормалізовано текст: {len(norm)} символів")
    
    # Крок 2: Підрахунок частот біграм
    bigrams = split_bigrams(norm)
    counter = Counter(bigrams)
    total = sum(counter.values())
    
    freqs = [(bg, cnt, cnt/total) for bg, cnt in counter.most_common()]
    cipher_top5 = [bg for bg, _, _ in freqs[:5]]
    
    # Таблиця біграм
    print(f"\n[Крок 2] 5 найчастіших біграм шифртексту:")
    print(f"{'№':<5} {'Біграма':<10} {'Кількість':<15} {'Частота (%)':<15}")
    for i, (bg, cnt, freq) in enumerate(freqs[:5], 1):
        print(f"{i:<5} {bg:<10} {cnt:<15} {freq*100:<15.4f}")
    
    # Збереження повної таблиці біграм у CSV
    with open('bigrams_table.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Номер', 'Біграма', 'Кількість', 'Частота'])
        for i, (bg, cnt, freq) in enumerate(freqs, 1):
            writer.writerow([i, bg, cnt, f"{freq:.6f}"])
    print("Таблиця біграм збережена у файл: bigrams_table.csv")
    
    print(f"\nБіграми російської мови: {', '.join(RUSSIAN_TOP5)}")
    
    # Крок 3: Генерація кандидатів
    print(f"\n[Крок 3] Генерація кандидатів на ключ...")
    candidates = generate_candidates(cipher_top5)
    print(f"Знайдено унікальних кандидатів: {len(candidates)}")
    
    # Збереження перших 40 кандидатів
    with open('candidates.txt', 'w', encoding='utf-8') as f:
        f.write("КАНДИДАТИ НА КЛЮЧ (перші 40)\n")
        f.write("=" * 50 + "\n\n")
        for i, (a, b) in enumerate(candidates[:40], 1):
            f.write(f"{i}. a={a}, b={b}\n")
    print("Кандидати збережені у файл: candidates.txt")
    
    # Крок 4: Розшифрування та пошук правильного ключа
    print(f"\n[Крок 4] Розшифрування та оцінка текстів...")
    results = []
    
    for idx, (a, b) in enumerate(candidates):
        dec = decrypt(norm, a, b)
        if dec:
            score = score_text(dec)
            results.append({'a': a, 'b': b, 'score': score, 'text': dec})
        if (idx + 1) % 100 == 0:
            print(f"    Перевірено {idx + 1}/{len(candidates)} кандидатів...")
    
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Збереження топ-10 результатів
    with open('top_results.txt', 'w', encoding='utf-8') as f:
        f.write("ТОП-10 РЕЗУЛЬТАТІВ\n")
        for i, r in enumerate(results[:10], 1):
            f.write(f"{i}. a={r['a']}, b={r['b']}, оцінка={r['score']:.2f}\n")
            f.write(f"   Текст: {r['text'][:100]}...\n\n")
    print("Топ-10 результатів збережено у файл: top_results.txt")
    
    # Крок 5: Найкращий результат
    if results:
        best = results[0]
        print("[Крок 5] ЗНАЙДЕНИЙ КЛЮЧ")
        print(f"a = {best['a']}")
        print(f"b = {best['b']}")
        print(f"Оцінка якості: {best['score']:.2f}")
        print(f"\nПерші 300 символів розшифрованого тексту:")
        print(best['text'][:300])
        
        # Збереження розшифрованого тексту
        with open('decrypted_text.txt', 'w', encoding='utf-8') as f:
            f.write(best['text'])
        print("\nПовний розшифрований текст збережено у файл: decrypted_text.txt")
        
        # Фінальний звіт
        with open('final_report.txt', 'w', encoding='utf-8') as f:
            f.write("ФІНАЛЬНИЙ ЗВІТ\n")
            f.write(f"Ключ шифрування: a={best['a']}, b={best['b']}\n\n")
            f.write("5 найчастіших біграм шифртексту:\n")
            for i, bg in enumerate(cipher_top5, 1):
                f.write(f"  {i}. {bg}\n")
            f.write(f"\nРозшифрований текст:\n{best['text']}\n")
        print("Фінальний звіт збережено у файл: final_report.txt")
        return best
    
    print("\nКлюч не знайдено!")
    return None


if __name__ == "__main__":
    try:
        analyze("09.txt")
    except FileNotFoundError:
        print("ПОМИЛКА: файл '09.txt' не знайдено!")
        print("Покладіть файл '09.txt' у ту ж папку, що й програма.")