import sys
import math
from collections import Counter
from typing import List, Tuple, Dict, Optional

class AffineBigramSolver:

    LETTERS = "абвгдежзийклмнопрстуфхцчшщьыэюя"
    M = len(LETTERS)             
    M_SQUARED = M * M            
    
    TOP_5_LANG_BIGRAMS = ["ст", "но", "то", "на", "ен"] 
    
    IMPOSSIBLE_BIGRAMS = [
        'аы', 'оы', 'иы', 'ыы', 'уы', 'еы', 'юы', 'яы', 'эы',
        'аь', 'оь', 'иь', 'ыь', 'уь', 'еь', 'юь', 'яь', 'эь'
    ]
    MAX_IMPOSSIBLE_OCCURRENCES = 2

    _letter_to_num: Dict[str, int] = {letter: index for index, letter in enumerate(LETTERS)}
    _num_to_letter: Dict[int, str] = {index: letter for index, letter in enumerate(LETTERS)}

    def __init__(self):
        if len(self._letter_to_num) != self.M:
            raise ValueError("Помилка ініціалізації: невідповідність довжини абетки.")

    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        g, x1, y1 = AffineBigramSolver.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return g, x, y

    def mod_inverse(self, a: int, m: int) -> Optional[int]:
        g, x, _ = self.extended_gcd(a, m)
        if g != 1:
            return None 
        return x % m
    
    def bigram_to_num(self, bg: str) -> int:
        return self._letter_to_num[bg[0]] * self.M + self._letter_to_num[bg[1]]

    def num_to_bigram(self, num: int) -> str:
        num = num % self.M_SQUARED 
        return self._num_to_letter[num // self.M] + self._num_to_letter[num % self.M]

    def decrypt(self, ciphertext: str, a: int, b: int) -> Optional[str]:
        a_inv = self.mod_inverse(a, self.M_SQUARED)
        if a_inv is None:
            return None

        plaintext_bigrams = []
        
        for i in range(0, len(ciphertext) - 1, 2):
            bg = ciphertext[i:i + 2]
            
            if bg[0] not in self._letter_to_num or bg[1] not in self._letter_to_num:
                continue 
                
            y = self.bigram_to_num(bg) 
            x = (a_inv * (y - b)) % self.M_SQUARED
            
            plaintext_bigrams.append(self.num_to_bigram(x))
            
        return "".join(plaintext_bigrams)

    def has_impossible_bigrams(self, text: str) -> bool:
        for bg in self.IMPOSSIBLE_BIGRAMS:
            if text.count(bg) > self.MAX_IMPOSSIBLE_OCCURRENCES:
                return True
        return False

    def calculate_ioc(self, text: str) -> float:
        counts = Counter(text)
        length = sum(counts.values())
        if length < 2:
            return 0.0
        
        numerator = sum(v * (v - 1) for v in counts.values())
        denominator = length * (length - 1)
        return numerator / denominator

    def get_top_bigrams(self, text: str, n: int = 5) -> List[str]:
        bigram_counts = Counter()
        for i in range(0, len(text) - 1, 2):
            if text[i] in self._letter_to_num and text[i + 1] in self._letter_to_num:
                bigram_counts[text[i:i + 2]] += 1
        
        return [bg for bg, _ in bigram_counts.most_common(n)]

    def _solve_for_a_candidates(self, x1: int, x2: int, y1: int, y2: int) -> List[int]:
        A = (x1 - x2) % self.M_SQUARED
        B = (y1 - y2) % self.M_SQUARED
        
        g = math.gcd(A, self.M_SQUARED)
        
        if B % g != 0:
            return []
            
        A_reduced = A // g
        B_reduced = B // g
        M_reduced = self.M_SQUARED // g
        
        inv_reduced = self.mod_inverse(A_reduced, M_reduced)
        if inv_reduced is None:
             return [] 
        
        a0 = (B_reduced * inv_reduced) % M_reduced
        
        return [(a0 + k * M_reduced) % self.M_SQUARED for k in range(g)]

    def find_key_candidates(self, cipher_top: List[str], lang_top: List[str]) -> List[Tuple[int, int]]:
        candidates = set()
        
        for i in range(len(cipher_top)):
            for j in range(len(cipher_top)):
                if i == j: continue
                
                for p in range(len(lang_top)):
                    for q in range(len(lang_top)):
                        if p == q: continue
                        
                        y1 = self.bigram_to_num(cipher_top[i])
                        y2 = self.bigram_to_num(cipher_top[j])
                        x1 = self.bigram_to_num(lang_top[p])
                        x2 = self.bigram_to_num(lang_top[q])
                        
                        a_list = self._solve_for_a_candidates(x1, x2, y1, y2)
                        
                        for a in a_list:
                            if math.gcd(a, self.M_SQUARED) != 1: 
                                continue
                            
                            b = (y1 - a * x1) % self.M_SQUARED
                            candidates.add((a, b))
                            
        return sorted(list(candidates))

def clean_and_prepare_text(text: str) -> str:
    text = text.lower().replace("ё", "е").replace("ъ", "ь")
    solver = AffineBigramSolver()
    cleaned_text = "".join(ch for ch in text if ch in solver._letter_to_num)
    
    if len(cleaned_text) % 2 != 0:
        cleaned_text = cleaned_text[:-1]
        
    return cleaned_text

def run_cryptanalysis():
    FILE_PATH = "11.txt"
    IC_THRESHOLD = 0.045
    
    try:
        with open(FILE_PATH, encoding="utf-8", errors="ignore") as f:
            ciphertext_raw = f.read()
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        sys.exit(1)

    ciphertext = clean_and_prepare_text(ciphertext_raw)
    solver = AffineBigramSolver()

    print("   Криптоаналіз Афінного Шифру (Біграми)   ")
    print(f"Довжина тексту = {len(ciphertext)}")

    cipher_top = solver.get_top_bigrams(ciphertext, n=5)
    print("Топ-5 біграм шифротексту:", cipher_top)

    candidates = solver.find_key_candidates(cipher_top, solver.TOP_5_LANG_BIGRAMS)
    print(f"Знайдено ключів-кандидатів = {len(candidates)}")

    valid_count = 0
    OUTPUT_FILE = "decrypted_result_lab.txt"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
        for a, b in candidates:
            decrypted_text = solver.decrypt(ciphertext, a, b)
            
            if decrypted_text is None:
                continue

            if solver.has_impossible_bigrams(decrypted_text):
                continue

            ic = solver.calculate_ioc(decrypted_text)
            if ic < IC_THRESHOLD: 
                continue

            valid_count += 1
            
            print(f"Кандидат №{valid_count}: a={a}, b={b}, IC={ic:.6f}")
            print(f"Розшифрування: {decrypted_text[:50]}...")
            
            
            fout.write(f"№{valid_count}  Ключ: a={a}, b={b}  IC={ic:.6f}\n")
            fout.write(decrypted_text)
            
    print(f"Кількість валідних: {valid_count}")
    print(f"Результати збережено у файлі '{OUTPUT_FILE}'")

if __name__ == "__main__":
    run_cryptanalysis()