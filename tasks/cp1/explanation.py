import math
import pandas as pd
from collections import Counter
# math — для математичних функцій, зокрема log2 для обчислення ентропії.
# pandas — для роботи з таблицями (DataFrame) та збереження у Excel.
# Counter — зручний інструмент для підрахунку частот елементів (літер, біграм).

# Ми обмежуємо текст лише буквами російського алфавіту + пробілом.
# Перетворення в нижній регістр дозволяє об’єднати великі та малі літери.
# Параметр with_spaces визначає, чи враховувати пробіли при обчисленні частот.
def clean_text(text, with_spaces=True):
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
    text = text.lower()  # Перетворюємо всі літери на нижній регістр
    text = "".join(ch for ch in text if ch in alphabet)  # Видаляємо все, що не в алфавіті
    if not with_spaces:
        text = text.replace(" ", "")  # Якщо не враховуємо пробіли, видаляємо їх
    return text

# Формуємо словник літера: частота.
# Частота літери = число появ літери / загальна кількість символів у тексті.
# Це і є імовірність появи символу для ентропії.
def letter_frequencies(text):
    total = len(text)
    counter = Counter(text)  # Підрахунок кількості кожної літери
    return {ch: counter[ch] / total for ch in sorted(counter)}  # Відносні частоти

# Біграми — це послідовності з 2 символів.
# overlap=True: біграми йдуть з кроком 1 → AB, BC, CD… (перетинаються)
# overlap=False: крок 2 → AB, CD, EF… (не перетинаються)
# Частота біграм = число появ біграми / загальна кількість біграм.
def bigram_frequencies(text, overlap=True):
    step = 1 if overlap else 2  # overlap=True -> перетинаючі біграми, інакше без перетину
    bigrams = [text[i:i+2] for i in range(0, len(text)-1, step)]
    total = len(bigrams)
    counter = Counter(bigrams)
    return {bg: counter[bg]/total for bg in counter}  # Відносні частоти біграм

# Ентропія Шеннона:  H = -сума (знизу і=1 зверху n) 𝑝𝑖 * log за основою 2 від 𝑝𝑖
# де 𝑝𝑖  — ймовірність появи символу (або біграми).
# Вона показує середню кількість біт інформації на символ.
# p > 0 — щоб уникнути логарифму від нуля.
def entropy(freqs):
    return -sum(p * math.log2(p) for p in freqs.values() if p > 0)

# Ентропія біграм на 1 символ = H(біграми) / 2, бо біграма складається з 2 символів.
# Таким чином отримуємо ентропію на символ, щоб можна було порівнювати з H1.
def entropy_bigrams(freqs):
    return entropy(freqs)/2

# Надлишковість (Redundancy) — це міра передбачуваності мови: формула є в протоколі R
# Наприклад, якщо всі символи зустрічаються рівномірно, R ≈ 0 (немає надлишковості).
# Для природної мови, де деякі літери зустрічаються частіше — R > 0.
def redundancy(H, alphabet_size):
    Hmax = math.log2(alphabet_size)
    return 1 - H / Hmax

# Створює матрицю частот біграм.
# Рядки → перший символ, стовпці → другий символ.
# Для кожної біграми ставимо її частоту у відповідну клітинку.
def bigram_matrix(freqs):
    letters = sorted(set("".join(freqs.keys())))  # Унікальні символи
    df = pd.DataFrame(0.0, index=letters, columns=letters)
    for bg, p in freqs.items():
        df.loc[bg[0], bg[1]] = round(p, 4)
    return df

# Спершу очищуємо текст (алфавіт + пробіли).
def analyze_text(text, with_spaces=True):
    text = clean_text(text, with_spaces)

# H1 — ентропія на символ для літер.
# R1 — надлишковість для 1-символьної моделі.
    letter_freq = letter_frequencies(text)
    H1 = entropy(letter_freq)
    R1 = redundancy(H1, len(letter_freq))

# Рахуємо частоти біграм з перетином та без.
    bigram_overlap = bigram_frequencies(text, overlap=True)
    bigram_nonoverlap = bigram_frequencies(text, overlap=False)

# Ентропія біграм на 1 символ.
    H2_overlap = entropy_bigrams(bigram_overlap)
    H2_nonoverlap = entropy_bigrams(bigram_nonoverlap)

# Надлишковість для моделей біграм з перетином та без.
# Чим більше R, тим мова передбачуваніша.
    R2_overlap = redundancy(H2_overlap, len(bigram_overlap))
    R2_nonoverlap = redundancy(H2_nonoverlap, len(bigram_nonoverlap))

# Повертаємо усі результати у словнику, зручному для Excel.
    return {
        "letters": letter_freq,
        "bigrams_overlap": bigram_overlap,
        "bigrams_nonoverlap": bigram_nonoverlap,
        "H1": H1, "R1": R1,
        "H2_overlap": H2_overlap, "R2_overlap": R2_overlap,
        "H2_nonoverlap": H2_nonoverlap, "R2_nonoverlap": R2_nonoverlap
    }

# Відкриваємо текст книги в UTF-8.
with open("Bulgakov_Mihail_Master_i_Margarita.txt", encoding="utf-8") as f:
    text = f.read()

# Розрахунок частот, ентропії та надлишковості для двох випадків:
# З пробілами
# Без пробілів
res_spaces = analyze_text(text, with_spaces=True)
res_nospaces = analyze_text(text, with_spaces=False)

# Зберігаємо частоти літер у Excel.
# sheet_name — назви аркушів.
with pd.ExcelWriter("crypto_analysis.xlsx") as writer:
    
    pd.DataFrame(list(res_spaces["letters"].items()), columns=["Літера", "Частота"]) \
        .to_excel(writer, sheet_name="Letters_Spaces", index=False)
    pd.DataFrame(list(res_nospaces["letters"].items()), columns=["Літера", "Частота"]) \
        .to_excel(writer, sheet_name="Letters_NoSpaces", index=False)

#     Зберігаємо матриці біграм:
# з перетином / без перетину
# з пробілами / без пробілів
    bigram_matrix(res_spaces["bigrams_overlap"]).to_excel(writer, sheet_name="Bigrams_Ov_Spaces")
    bigram_matrix(res_spaces["bigrams_nonoverlap"]).to_excel(writer, sheet_name="Bigrams_NonOv_Spaces")
    bigram_matrix(res_nospaces["bigrams_overlap"]).to_excel(writer, sheet_name="Bigrams_Ov_NoSpaces")
    bigram_matrix(res_nospaces["bigrams_nonoverlap"]).to_excel(writer, sheet_name="Bigrams_NonOv_NoSpaces")

# Створюємо зведену таблицю з ентропіями і надлишковістю для всіх моделей.
# round(..., 5) — для акуратного відображення результатів.
    summary = pd.DataFrame({
        "Метрика": ["H1", "R1", "H2_Перетин", "R2_Перетин", "H2_Без_Перетин", "R2_Без_Перетин"],
        "З пробілами": [
            round(res_spaces["H1"], 5), round(res_spaces["R1"], 5),
            round(res_spaces["H2_overlap"], 5), round(res_spaces["R2_overlap"], 5),
            round(res_spaces["H2_nonoverlap"], 5), round(res_spaces["R2_nonoverlap"], 5)
        ],
        "Без пробілів": [
            round(res_nospaces["H1"], 5), round(res_nospaces["R1"], 5),
            round(res_nospaces["H2_overlap"], 5), round(res_nospaces["R2_overlap"], 5),
            round(res_nospaces["H2_nonoverlap"], 5), round(res_nospaces["R2_nonoverlap"], 5)
        ]
    })
    summary.to_excel(writer, sheet_name="Summary", index=False)

print("Result saved to crypto_analysis.xlsx")