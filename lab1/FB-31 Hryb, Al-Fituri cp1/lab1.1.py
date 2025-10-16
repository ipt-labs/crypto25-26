# -*- coding: utf-8 -*-
import sys, math
from collections import Counter
from pathlib import Path
import pandas as pd # type: ignore

# ===== НАЛАШТУВАННЯ =====
EXCEL_OUT = "crypto_5tables.xlsx"   # вихідний Excel-файл
# Російський алфавіт (малі літери); заміна "ё" → "е", "ъ" → "ь"
RUS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====
def clean_text(s: str, keep_space: bool) -> str:
    """
    Приведення до нижнього регістру; заміни: ё→е, ъ→ь.
    Якщо keep_space=True, усі пропуски (пробіли, таби, нові рядки) замінюються одним звичайним пробілом.
    Якщо keep_space=False — усі пропуски прибираються повністю.
    Потім залишаються лише дозволені символи (літери +, за потреби, пробіл).
    """
    s = s.lower().replace("ё", "е").replace("ъ", "ь")

    if keep_space:
        s = " ".join(s.split())
    else:
        s = "".join(s.split())

    allowed = set(RUS.replace("ё","е").replace("ъ","ь") + (" " if keep_space else ""))
    return "".join(ch for ch in s if ch in allowed)


def freq_letters_df(txt: str, include_space: bool) -> pd.DataFrame:
    """Підрахунок частот літер"""
    cnt = Counter(txt)
    rows = []
    if include_space:
        total = sum(cnt.values())
        for ch in (RUS.replace("ё","е").replace("ъ","ь") + " "):
            if ch in cnt:
                name = "пробіл" if ch == " " else ch
                rows.append([name, cnt[ch], cnt[ch]/total])
    else:
        total = sum(cnt[ch] for ch in RUS if ch in cnt)
        for ch in RUS:
            if ch in cnt:
                rows.append([ch, cnt[ch], cnt[ch]/total])
    df = pd.DataFrame(rows, columns=["Літера","Кількість","Частота"])
    return df.sort_values("Частота", ascending=False).reset_index(drop=True)


def bigram_freq(txt: str, overlap: bool) -> dict[str,float]:
    """Частоти біграм; overlap=True → крок 1, інакше — крок 2"""
    step = 1 if overlap else 2
    pairs = [txt[i:i+2] for i in range(0, len(txt)-1, step) if len(txt[i:i+2]) == 2]
    cnt = Counter(pairs)
    total = sum(cnt.values()) or 1
    return {bg: cnt[bg]/total for bg in cnt}


def bigram_matrix(freq: dict[str,float], include_space: bool) -> pd.DataFrame:
    """Матриця біграм (рядок — перша літера, стовпець — друга)"""
    letters = list(RUS.replace("ё","е").replace("ъ","ь") + (" " if include_space else ""))
    df = pd.DataFrame(0.0, index=letters, columns=letters)
    for bg, p in freq.items():
        a, b = bg[0], bg[1]
        if a in df.index and b in df.columns:
            df.at[a, b] = round(p, 6)
    if include_space:
        df.rename(index={" ":"пробіл"}, columns={" ":"пробіл"}, inplace=True)
    return df


def entropy_from_freq(freq: dict[str,float]) -> float:
    """H = -∑ p log2 p"""
    return -sum(p * math.log2(p) for p in freq.values() if p > 0)


def redundancy(H: float, m: int) -> float:
    """R = 1 - H / log2(m)"""
    return 1.0 - H / math.log2(m)


# ===== ОСНОВНА ЛОГІКА =====
def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else "lab1bookru.txt"
    p = Path(infile)
    if not p.exists():
        raise FileNotFoundError(f"Файл не знайдено: {infile}")

    raw = p.read_text(encoding="utf-8", errors="ignore")
    print(f"Розмір вхідного тексту: {len(raw)/1024/1024:.2f} МБ")

    # Очищення тексту
    txt_with_space = clean_text(raw, keep_space=True)
    txt_no_space   = clean_text(raw, keep_space=False)

    # === ІНФОРМАЦІЯ ДЛЯ ПЕРЕВІРКИ ===
    print("=== ІНФОРМАЦІЯ ПРО ОЧИЩЕНИЙ ТЕКСТ ===")
    print("Довжина початкового тексту =", len(raw))
    print("Довжина з пробілами =", len(txt_with_space))
    print("Кількість пробілів =", txt_with_space.count(' '))
    print("Довжина без пробілів =", len(txt_no_space))
    print("Приклад з пробілами:", repr(txt_with_space[:200]))
    print("Приклад без пробілів:", repr(txt_no_space[:200]))
    print("=====================================")

    # Запис очищених версій у файли
    with open("cleaned_with_space.txt", "w", encoding="utf-8") as f:
        f.write(txt_with_space)
    with open("cleaned_no_space.txt", "w", encoding="utf-8") as f:
        f.write(txt_no_space)

    # 1) Частоти літер
    df_letters_S  = freq_letters_df(txt_with_space, include_space=True)
    df_letters_NS = freq_letters_df(txt_no_space,   include_space=False)

    # 2) Біграми (4 варіанти)
    bf_S_ov   = bigram_freq(txt_with_space, overlap=True)
    bf_S_noov = bigram_freq(txt_with_space, overlap=False)
    bf_NS_ov   = bigram_freq(txt_no_space, overlap=True)
    bf_NS_noov = bigram_freq(txt_no_space, overlap=False)

    M_S_ov    = bigram_matrix(bf_S_ov,    include_space=True)
    M_S_noov  = bigram_matrix(bf_S_noov,  include_space=True)
    M_NS_ov   = bigram_matrix(bf_NS_ov,   include_space=False)
    M_NS_noov = bigram_matrix(bf_NS_noov, include_space=False)

    # 3) Ентропія та надлишковість
    letter_freq_S_incl_space = {ch: c/len(txt_with_space) for ch, c in Counter(txt_with_space).items()}
    letter_freq_NS = {ch: c/len(txt_no_space) for ch, c in Counter(txt_no_space).items()}

    H1_S  = entropy_from_freq(letter_freq_S_incl_space)
    H1_NS = entropy_from_freq(letter_freq_NS)

    H2_S_ov    = entropy_from_freq(bf_S_ov)/2.0    if bf_S_ov    else 0.0
    H2_S_noov  = entropy_from_freq(bf_S_noov)/2.0  if bf_S_noov  else 0.0
    H2_NS_ov   = entropy_from_freq(bf_NS_ov)/2.0   if bf_NS_ov   else 0.0
    H2_NS_noov = entropy_from_freq(bf_NS_noov)/2.0 if bf_NS_noov else 0.0

    R1_S       = redundancy(H1_S,      m=33)
    R1_NS      = redundancy(H1_NS,     m=32)
    R2_S_ov    = redundancy(H2_S_ov,   m=33)
    R2_S_noov  = redundancy(H2_S_noov, m=33)
    R2_NS_ov   = redundancy(H2_NS_ov,  m=32)
    R2_NS_noov = redundancy(H2_NS_noov,m=32)

    df_sum = pd.DataFrame({
        "Показник": [
            "H1", "R1",
            "H2 (з перекриттям)", "R2 (з перекриттям)",
            "H2 (без перекриття)", "R2 (без перекриття)"
        ],
        "З пробілами": [
            round(H1_S,6), round(R1_S,6),
            round(H2_S_ov,6),   round(R2_S_ov,6),
            round(H2_S_noov,6), round(R2_S_noov,6),
        ],
        "Без пробілів": [
            round(H1_NS,6), round(R1_NS,6),
            round(H2_NS_ov,6),   round(R2_NS_ov,6),
            round(H2_NS_noov,6), round(R2_NS_noov,6),
        ],
    })

    # Виведення у консоль
    print("\n=== З ПРОБІЛАМИ ===")
    print(f"H1 = {H1_S:.6f} | R1 = {R1_S:.6f}")
    print(f"H2 (з перекриттям) = {H2_S_ov:.6f} | R2 (з перекриттям) = {R2_S_ov:.6f}")
    print(f"H2 (без перекриття) = {H2_S_noov:.6f} | R2 (без перекриття) = {R2_S_noov:.6f}")

    print("\n=== БЕЗ ПРОБІЛІВ ===")
    print(f"H1 = {H1_NS:.6f} | R1 = {R1_NS:.6f}")
    print(f"H2 (з перекриттям) = {H2_NS_ov:.6f} | R2 (з перекриттям) = {R2_NS_ov:.6f}")
    print(f"H2 (без перекриття) = {H2_NS_noov:.6f} | R2 (без перекриття) = {R2_NS_noov:.6f}")

    # 4) Запис у Excel (7 аркушів)
    with pd.ExcelWriter(EXCEL_OUT) as w:
        df_letters_S.to_excel( w, sheet_name="1_Літери_з_пробілами", index=False)
        df_letters_NS.to_excel(w, sheet_name="2_Літери_без_пробілів", index=False)
        M_S_ov.to_excel(    w, sheet_name="3_Біграми_з_перекриттям_з_пробілами")
        M_S_noov.to_excel(  w, sheet_name="4_Біграми_без_перекриття_з_пробілами")
        M_NS_ov.to_excel(   w, sheet_name="5_Біграми_з_перекриттям_без_пробілів")
        M_NS_noov.to_excel( w, sheet_name="6_Біграми_без_перекриття_без_пробілів")
        df_sum.to_excel(w,  sheet_name="7_Підсумок", index=False)

    print(f"\nСтворено файл '{EXCEL_OUT}' з 7 аркушами.")


if __name__ == "__main__":
    main()
