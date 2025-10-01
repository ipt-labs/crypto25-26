# lab1_final.py
import re
import math
from collections import Counter
import pandas as pd
import os
import random

# ====================================================================================
# ЧАСТИНА 1: Клас для автоматичного розрахунку H1 та H2
# ====================================================================================

class TextStatistics:
    """Клас для обчислення статистичних характеристик тексту (частоти, ентропії, надлишковість)."""

    def __init__(self, raw_text: str, keep_spaces: bool = True):
        if not raw_text:
            raise ValueError("Порожній текст!")

        self.text = self._clean_text(raw_text, keep_spaces)
        self.keep_spaces = keep_spaces
        self.alphabet = sorted(list(set(self.text)))
        self.alphabet_size = len(self.alphabet)

        self.letter_freq = self._letter_frequencies()
        self.bigram_freq_overlap, self.bigram_freq_non_overlap = self._bigram_frequencies()

    @staticmethod
    def _clean_text(text: str, keep_spaces: bool) -> str:
        text = text.lower()
        text = re.sub(r'[^а-яё ]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        if not keep_spaces:
            text = text.replace(" ", "")
        return text.strip()

    def _letter_frequencies(self) -> dict:
        counter = Counter(self.text)
        total = len(self.text)
        return {ch: counter[ch] / total for ch in self.alphabet}

    def _bigram_frequencies(self):
        n = len(self.text)
        overlap = Counter(self.text[i:i + 2] for i in range(n - 1) if len(self.text[i:i + 2]) == 2)
        non_overlap = Counter(self.text[i:i + 2] for i in range(0, n - 1, 2) if len(self.text[i:i + 2]) == 2)

        total_overlap = sum(overlap.values())
        total_non_overlap = sum(non_overlap.values())

        freq_overlap = {bg: overlap[bg] / total_overlap for bg in overlap}
        freq_non_overlap = {bg: non_overlap[bg] / total_non_overlap for bg in non_overlap}

        return freq_overlap, freq_non_overlap

    @staticmethod
    def _entropy(freqs: dict, n_gram: int = 1) -> float:
        h = -sum(p * math.log2(p) for p in freqs.values() if p > 0)
        return h / n_gram

    def get_h1(self) -> float:
        return self._entropy(self.letter_freq, 1)

    def get_h2(self, overlap: bool = True) -> float:
        freqs = self.bigram_freq_overlap if overlap else self.bigram_freq_non_overlap
        return self._entropy(freqs, 2)

    def get_redundancy(self, entropy_value: float) -> float:
        max_entropy = math.log2(self.alphabet_size)
        if max_entropy == 0: return 0
        return 1 - (entropy_value / max_entropy)

    def letter_table(self, sort_by="frequency") -> pd.DataFrame:
        df = pd.DataFrame(list(self.letter_freq.items()), columns=["Символ", "Частота"])
        if sort_by == "alphabet":
            df = df.sort_values(by="Символ")
        elif sort_by == "frequency":
            df = df.sort_values(by="Частота", ascending=False)
        return df

    def bigram_matrix(self, overlap: bool = True) -> pd.DataFrame:
        freq = self.bigram_freq_overlap if overlap else self.bigram_freq_non_overlap
        symbols = self.alphabet
        matrix = pd.DataFrame(0.0, index=symbols, columns=symbols)
        for bg, val in freq.items():
            if len(bg) == 2:
                matrix.at[bg[0], bg[1]] = round(val, 5)
        return matrix

# ====================================================================================
# ЧАСТИНА 2: Функції для інтерактивної оцінки H(n)
# ====================================================================================

def run_guessing_experiment(text: str, n: int, num_experiments: int, alphabet: list):
    print(f"\n===== Починаємо експеримент для H({n}) на {num_experiments} спробах =====")
    print("Ваше завдання: вгадати наступну літеру після показаного фрагмента тексту.")
    guess_attempts = []
    for i in range(num_experiments):
        start_pos = random.randint(0, len(text) - n - 1)
        context = text[start_pos : start_pos + n - 1]
        correct_char = text[start_pos + n - 1]
        
        print(f"\n--- Експеримент [{i+1}/{num_experiments}] ---")
        print(f"Контекст: ...{context}")
        
        attempts = 0
        guessed_chars = set()
        while True:
            try:
                guess = input("Ваша спроба (введіть одну літеру): ").lower()
            except EOFError:
                print("\nЕксперимент перервано.")
                return None

            if len(guess) != 1 or guess not in alphabet:
                print("Будь ласка, введіть одну кириличну літеру або пробіл.")
                continue
            
            if guess in guessed_chars:
                print(f"Ви вже пробували літеру '{guess}'. Спробуйте іншу.")
                continue

            attempts += 1
            guessed_chars.add(guess)
            if guess == correct_char:
                print(f"Правильно! Кількість спроб: {attempts}")
                guess_attempts.append(attempts)
                break
            else:
                print("Неправильно, спробуйте ще раз.")
    return guess_attempts

def calculate_h_n_bounds(attempts_list: list, alphabet_size: int):
    if not attempts_list:
        print("Список результатів порожній. Розрахунок неможливий.")
        return

    num_experiments = len(attempts_list)
    counts = Counter(attempts_list)
    q = {i: counts.get(i, 0) / num_experiments for i in range(1, alphabet_size + 1)}

    h_upper = -sum(p * math.log2(p) for p in q.values() if p > 0)
    
    h_lower = 0
    for i in range(1, alphabet_size):
        term = i * (q.get(i, 0) - q.get(i + 1, 0)) * math.log2(i) if i > 0 else 0
        h_lower += term
    h_lower += alphabet_size * q.get(alphabet_size, 0) * math.log2(alphabet_size)

    print("\n===== Результати експерименту =====")
    print(f"Розподіл кількості спроб (спроба: кількість разів): {sorted(counts.items())}")
    print("\nОцінка умовної ентропії H(n):")
    print(f"Нижня межа: {h_lower:.4f}")
    print(f"Верхня межа: {h_upper:.4f}")
    print(f"Середнє значення: {(h_lower + h_upper) / 2:.4f}")

# ====================================================================================
# ЧАСТИНА 3: Функції для збереження та запуску
# ====================================================================================

def save_results_to_excel(writer, analyzer_with_spaces, analyzer_no_spaces, summary_df):
    print("\nЗбереження результатів у Excel...")
    summary_df.to_excel(writer, sheet_name="Зведена таблиця", index=False)
    analyzer_with_spaces.letter_table(sort_by="frequency").to_excel(
        writer, sheet_name="Літери_Частота_з_пробілами", index=False
    )
    analyzer_with_spaces.bigram_matrix(overlap=True).to_excel(
        writer, sheet_name="Біграми_Перетин_з_пробілами"
    )
    analyzer_with_spaces.bigram_matrix(overlap=False).to_excel(
        writer, sheet_name="Біграми_БезПеретину_з_пробілами"
    )
    analyzer_no_spaces.letter_table(sort_by="frequency").to_excel(
        writer, sheet_name="Літери_Частота_без_пробілів", index=False
    )
    analyzer_no_spaces.bigram_matrix(overlap=True).to_excel(
        writer, sheet_name="Біграми_Перетин_без_пробілів"
    )
    analyzer_no_spaces.bigram_matrix(overlap=False).to_excel(
        writer, sheet_name="Біграми_БезПеретину_без_пробілів"
    )
    print("Збереження завершено.")

def main():
    # --- Крок 1.1: Автоматичний аналіз H1 та H2 ---
    print("===== Початок автоматичного аналізу тексту (H1, H2) =====")
    try:
        with open("book.txt", "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print("Помилка: файл 'book.txt' не знайдено! Переконайтесь, що він знаходиться в одній папці зі скриптом.")
        return

    analyzer_with_spaces = TextStatistics(raw_text, keep_spaces=True)
    analyzer_no_spaces = TextStatistics(raw_text, keep_spaces=False)

    # --- З ПРОБІЛАМИ ---
    h1_ws = analyzer_with_spaces.get_h1()
    r1_ws = analyzer_with_spaces.get_redundancy(h1_ws)
    h2_ws_overlap = analyzer_with_spaces.get_h2(overlap=True)
    r2_ws_overlap = analyzer_with_spaces.get_redundancy(h2_ws_overlap)
    h2_ws_non_overlap = analyzer_with_spaces.get_h2(overlap=False) 
    r2_ws_non_overlap = analyzer_with_spaces.get_redundancy(h2_ws_non_overlap) 

    # --- БЕЗ ПРОБІЛІВ ---
    h1_ns = analyzer_no_spaces.get_h1()
    r1_ns = analyzer_no_spaces.get_redundancy(h1_ns)
    h2_ns_overlap = analyzer_no_spaces.get_h2(overlap=True)
    r2_ns_overlap = analyzer_no_spaces.get_redundancy(h2_ns_overlap)
    h2_ns_non_overlap = analyzer_no_spaces.get_h2(overlap=False) 
    r2_ns_non_overlap = analyzer_no_spaces.get_redundancy(h2_ns_non_overlap) 

    # --- ОНОВЛЕНА ТАБЛИЦЯ ---
    summary_df = pd.DataFrame({
        "Метрика": [
            "H1",
            "R1 (для H1)",
            "H2 (з перетином)",
            "R2 (для H2 з перетином)",
            "H2 (БЕЗ перетину)",
            "R2 (для H2 без перетину)"
        ],
        "З пробілами": [
            f"{h1_ws:.4f}", f"{r1_ws:.4f}",
            f"{h2_ws_overlap:.4f}", f"{r2_ws_overlap:.4f}",
            f"{h2_ws_non_overlap:.4f}", f"{r2_ws_non_overlap:.4f}" 
        ],
        "Без пробілів": [
            f"{h1_ns:.4f}", f"{r1_ns:.4f}",
            f"{h2_ns_overlap:.4f}", f"{r2_ns_overlap:.4f}",
            f"{h2_ns_non_overlap:.4f}", f"{r2_ns_non_overlap:.4f}" 
        ],
    })

    print("\nЗведена таблиця автоматичних розрахунків:")
    print(summary_df)
    
    # --- Крок 1.2: Експорт результатів у Excel ---
    out_path = "lab1_analysis_results.xlsx"
    try:
        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            save_results_to_excel(writer, analyzer_with_spaces, analyzer_no_spaces, summary_df)
        print(f"\nАналіз успішно збережено у файл: {out_path}")
    except PermissionError:
        print(f"\n[ПОПЕРЕДЖЕННЯ] Файл {out_path} зайнятий. Неможливо записати.")
        alt_path = "lab1_analysis_results_COPY.xlsx"
        try:
            with pd.ExcelWriter(alt_path, engine="openpyxl") as writer:
                save_results_to_excel(writer, analyzer_with_spaces, analyzer_no_spaces, summary_df)
            print(f"Результати збережено в альтернативний файл: {alt_path}")
        except Exception as e:
            print(f"Не вдалося зберегти навіть у копію. Помилка: {e}")
    except Exception as e:
        print(f"Сталася помилка при збереженні в Excel: {e}")

    # --- Крок 2: Інтерактивний експеримент для H(n) ---
    print("\n" + "="*25)
    print("Переходимо до інтерактивного експерименту (H(n))")
    print("="*25)
    
    processed_text_for_exp = analyzer_with_spaces.text
    alphabet_for_exp = analyzer_with_spaces.alphabet
    alphabet_size = analyzer_with_spaces.alphabet_size
    NUM_EXPERIMENTS = 50
    
    while True:
        choice = input("\nДля якого 'n' провести експеримент? (10, 20, 30, або 'exit' для виходу): ")
        if choice.lower() in ['exit', 'вихід', 'e', 'q']:
            break
        if choice not in ['10', '20', '30']:
            print("Неправильний вибір. Введіть 10, 20 або 30.")
            continue
            
        n = int(choice)
        attempts = run_guessing_experiment(processed_text_for_exp, n, NUM_EXPERIMENTS, alphabet_for_exp)
        
        if attempts:
            calculate_h_n_bounds(attempts, alphabet_size)

    print("\nРоботу завершено.")

if __name__ == "__main__":
    main()