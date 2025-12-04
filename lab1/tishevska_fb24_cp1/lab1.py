from collections import Counter, defaultdict
from math import log2
import csv
import os
import re
from typing import Dict, List

# Алфавіти
ALPHABET_WITH_SPACE = "абвгдежзийклмнопрстуфхцчшщыьэюя "
ALPHABET_NO_SPACE = "абвгдежзийклмнопрстуфхцчшщыьэюя"

# Вхідний файл
INPUT_PATH = "text.txt"

# Каталог для результатів
OUT_DIR = "результати"
os.makedirs(OUT_DIR, exist_ok=True)


# =========================
# 1. Зчитування та нормалізація
# =========================
def read_text_auto(path: str) -> str:
    for enc in ("utf-8", "cp1251"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("read_text_auto", b"", 0, 1, "Не вдалося відкрити файл у відомих кодуваннях")


def normalize_with_space(raw: str) -> str:
    t = raw.replace("ё", "е").replace("Ё", "Е").replace("ъ", "ь").replace("Ъ", "Ь").lower()
    t = re.sub(r"[^а-я\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def remove_spaces(text: str) -> str:
    return text.replace(" ", "")


# =========================
# 2. Підрахунок частот
# =========================
def monogram_counts(text: str) -> Counter:
    return Counter(text)


def counts_to_freqs(counts: Dict[str, int], total: int) -> Dict[str, float]:
    if total == 0:
        return {}
    return {k: v / total for k, v in counts.items()}


def bigram_counts(text: str, step: int) -> Dict[str, int]:
    res: Dict[str, int] = defaultdict(int)
    for i in range(0, len(text) - 1, step):
        bg = text[i:i + 2]
        if len(bg) == 2:
            res[bg] += 1
    return dict(res)


def bigram_freqs(bi_counts: Dict[str, int]) -> Dict[str, float]:
    total = sum(bi_counts.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in bi_counts.items()}


# =========================
# 3. Ентропія та надлишковість
# =========================
def shannon_entropy(freqs: Dict[str, float], divide_by: int = 1) -> float:
    h = 0.0
    for p in freqs.values():
        if p > 0:
            h -= p * log2(p)
    return h / divide_by if divide_by > 1 else h


def redundancy(h: float, alphabet_size: int) -> float:
    return 1 - (h / log2(alphabet_size)) if alphabet_size > 1 else 0


# =========================
# 4. Запис CSV 
# =========================
def write_letter_table_sorted(path: str, freqs: Dict[str, float], counts: Dict[str, int]):
    """Відсортована таблиця частот букв."""
    items = sorted(freqs.items(), key=lambda kv: (-kv[1], kv[0]))
    with open(path, "w", encoding="cp1251", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Символ", "Кількість", "Частота"])
        for ch, freq in items:
            writer.writerow([ch, counts[ch], freq])


def write_bigram_matrix(path: str, freqs: Dict[str, float], alphabet: str):
    """Квадратна матриця частот біграм."""
    with open(path, "w", encoding="cp1251", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([" "] + list(alphabet))
        for a1 in alphabet:
            row = [freqs.get(a1 + a2, 0.0) for a2 in alphabet]
            writer.writerow([a1] + row)


# =========================
# 5. Основна логіка
# =========================
def main():
    # Перевірка довжини файлу ≥ 1 МБ
    size = os.path.getsize(INPUT_PATH)
    assert size >= 1 * 1024 * 1024, f"Файл занадто малий ({size} байт), потрібно ≥ 1 МБ"

    raw = read_text_auto(INPUT_PATH)
    text_sp = normalize_with_space(raw)
    text_nsp = remove_spaces(text_sp)

    # Монограми
    mono_counts_sp = monogram_counts(text_sp)
    mono_freqs_sp = counts_to_freqs(mono_counts_sp, len(text_sp))
    H1_sp = shannon_entropy(mono_freqs_sp)
    R1_sp = redundancy(H1_sp, len(ALPHABET_WITH_SPACE))

    mono_counts_nsp = monogram_counts(text_nsp)
    mono_freqs_nsp = counts_to_freqs(mono_counts_nsp, len(text_nsp))
    H1_nsp = shannon_entropy(mono_freqs_nsp)
    R1_nsp = redundancy(H1_nsp, len(ALPHABET_NO_SPACE))

    # Біграми step=1 (перетинні)
    bi_counts_step1_sp = bigram_counts(text_sp, step=1)
    bi_freqs_step1_sp = bigram_freqs(bi_counts_step1_sp)
    H2_step1_sp = shannon_entropy(bi_freqs_step1_sp, divide_by=2)
    R2_step1_sp = redundancy(H2_step1_sp, len(ALPHABET_WITH_SPACE))

    bi_counts_step1_nsp = bigram_counts(text_nsp, step=1)
    bi_freqs_step1_nsp = bigram_freqs(bi_counts_step1_nsp)
    H2_step1_nsp = shannon_entropy(bi_freqs_step1_nsp, divide_by=2)
    R2_step1_nsp = redundancy(H2_step1_nsp, len(ALPHABET_NO_SPACE))

    # Біграми step=2 (неперетинні) 
    bi_counts_step2_sp = bigram_counts(text_sp, step=2)
    bi_freqs_step2_sp = bigram_freqs(bi_counts_step2_sp)
    H2_step2_sp = shannon_entropy(bi_freqs_step2_sp, divide_by=2)
    R2_step2_sp = redundancy(H2_step2_sp, len(ALPHABET_WITH_SPACE))

    bi_counts_step2_nsp = bigram_counts(text_nsp, step=2)
    bi_freqs_step2_nsp = bigram_freqs(bi_counts_step2_nsp)
    H2_step2_nsp = shannon_entropy(bi_freqs_step2_nsp, divide_by=2)
    R2_step2_nsp = redundancy(H2_step2_nsp, len(ALPHABET_NO_SPACE))

    # Вивід результатів 
    print("-" * 50)
    print(f"Довжина тексту (з пробілами): {len(text_sp)}")
    print(f"Довжина тексту (без пробілів): {len(text_nsp)}")
    print("-" * 50)
    print(f"H1 (з пробілом): {H1_sp:.8f} | R1 = {R1_sp:.8f}")
    print(f"H1 (без пробілів): {H1_nsp:.8f} | R1 = {R1_nsp:.8f}")
    print("-" * 50)
    print(f"H2 step=1 (з пробілом): {H2_step1_sp:.8f} | R2 = {R2_step1_sp:.8f}")
    print(f"H2 step=1 (без пробілів): {H2_step1_nsp:.8f} | R2 = {R2_step1_nsp:.8f}")
    print(f"H2 step=2 (з пробілом): {H2_step2_sp:.8f} | R2 = {R2_step2_sp:.8f}")
    print(f"H2 step=2 (без пробілів): {H2_step2_nsp:.8f} | R2 = {R2_step2_nsp:.8f}")
    print("-" * 50)

    # Збереження таблиць
    write_letter_table_sorted(
        os.path.join(OUT_DIR, "Моно_з_пробілами.csv"),
        mono_freqs_sp,
        mono_counts_sp
    )
    write_letter_table_sorted(
        os.path.join(OUT_DIR, "Моно_без_пробілів.csv"),
        mono_freqs_nsp,
        mono_counts_nsp
    )

    #  Матриці біграм
    write_bigram_matrix(
        os.path.join(OUT_DIR, "Біграми_step1_з_пробілами.csv"),
        bi_freqs_step1_sp,
        ALPHABET_WITH_SPACE
    )
    write_bigram_matrix(
        os.path.join(OUT_DIR, "Біграми_step1_без_пробілів.csv"),
        bi_freqs_step1_nsp,
        ALPHABET_NO_SPACE
    )
    write_bigram_matrix(
        os.path.join(OUT_DIR, "Біграми_step2_з_пробілами.csv"),
        bi_freqs_step2_sp,
        ALPHABET_WITH_SPACE
    )
    write_bigram_matrix(
        os.path.join(OUT_DIR, "Біграми_step2_без_пробілів.csv"),
        bi_freqs_step2_nsp,
        ALPHABET_NO_SPACE
    )


if __name__ == "__main__":
    main()
