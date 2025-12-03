from collections import Counter
from itertools import permutations
import math
import os
import sys

ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
N = len(ALPHABET)
MOD = N * N

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    x, y = y1, x1 - (a // b) * y1
    return g, x, y

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

def solve_linear_congruence(a, b, m):
    g = math.gcd(a, m)
    if b % g != 0:
        return []
    a1, b1, m1 = a // g, b // g, m // g
    inv = modinv(a1, m1)
    if inv is None:
        return []
    x0 = (inv * b1) % m1
    return [(x0 + i * m1) % m for i in range(g)]

def bi_nonoverlap(text):
    return [text[i:i+2] for i in range(0, len(text)-1, 2)]

def bigram_to_num(bg):
    return ALPHABET.index(bg[0]) * N + ALPHABET.index(bg[1])

def num_to_bigram(num):
    return ALPHABET[num // N] + ALPHABET[num % N]

def clean_text(text):
    text = text.lower().replace("ё", "е").replace("ъ", "ь")
    return ''.join(ch for ch in text if ch in ALPHABET)

class TextStatistics:
    def __init__(self, text):
        self.text = text
        self.letter_freq = self._letter_freq()
        self.bigram_freq = self._bigram_freq()
        self.trigram_freq = self._trigram_freq()

    def _letter_freq(self):
        cnt = Counter(self.text)
        total = len(self.text) if len(self.text) > 0 else 1
        return {ch: cnt[ch]/total for ch in cnt}

    def _bigram_freq(self):
        bigrams = bi_nonoverlap(self.text)
        cnt = Counter(bigrams)
        total = sum(cnt.values()) if sum(cnt.values()) > 0 else 1
        return {bg: cnt[bg]/total for bg in cnt}

    def _trigram_freq(self):
        trigrams = [self.text[i:i+3] for i in range(len(self.text)-2)]
        cnt = Counter(trigrams)
        total = sum(cnt.values()) if sum(cnt.values()) > 0 else 1
        return {tg: cnt[tg]/total for tg in cnt}

def decrypt_affine_bigram(ciphertext, a, b):
    inv_a = modinv(a, MOD)
    if inv_a is None:
        return None
    plain = []
    for bg in bi_nonoverlap(ciphertext):
        if len(bg) != 2:
            continue
        y = bigram_to_num(bg)
        x = (inv_a * (y - b)) % MOD
        plain.append(num_to_bigram(x))
    return ''.join(plain)

def score_russian_likeness(text):
    ts = TextStatistics(text)
    freq_common = sum(ts.letter_freq.get(ch, 0) for ch in "оеа")
    top_bigrams = ["ст","но","то","на","ен"]
    bg_score = sum(ts.bigram_freq.get(bg,0) for bg in top_bigrams)
    top_trigrams = ["сто","ест","ова","ени","ние"]
    tg_score = sum(ts.trigram_freq.get(tg,0) for tg in top_trigrams)
    total_score = freq_common*100 + bg_score*1000 + tg_score*2000
    return total_score

def attack_affine_bigram_improved(ciphertext, candidates_out="candidates.txt", decrypted_out="decrypted.txt"):
    open(candidates_out, "w", encoding="utf-8").close()
    open(decrypted_out, "w", encoding="utf-8").close()

    nonover = bi_nonoverlap(ciphertext)
    ctr = Counter(nonover)
    top5 = ctr.most_common(5)
    print("ТОП-5 біграм шифртексту (неперекриті):")
    total_nonover = len(nonover) if len(nonover) > 0 else 1
    for bg, cnt in top5:
        pct = cnt / total_nonover * 100
        print(f"  {bg}: {cnt} входжень  ({pct:.3f}%)")

    top_cipher_bigrams = [bg for bg,_ in top5]
    top_rus_bigrams = ["ст","но","то","на","ен"]

    logged_keys = set()
    keys_list = []

    for plain_pair in permutations(top_rus_bigrams, 2):
        x1 = bigram_to_num(plain_pair[0])
        x2 = bigram_to_num(plain_pair[1])
        for cipher_pair in permutations(top_cipher_bigrams, 2):
            y1 = bigram_to_num(cipher_pair[0])
            y2 = bigram_to_num(cipher_pair[1])
            a_candidates = solve_linear_congruence((x2 - x1) % MOD, (y2 - y1) % MOD, MOD)
            for a in a_candidates:
                b = (y1 - a * x1) % MOD
                if (a,b) in logged_keys:
                    continue
                logged_keys.add((a,b))
                keys_list.append((a,b))

    total_keys = len(keys_list)
    if total_keys == 0:
        print("Не знайдено кандидатів ключів.")
        return

    candidates_data = []
    for idx, (a,b) in enumerate(keys_list, start=1):
        print(f"Перевірка кандидата {idx}/{total_keys}...", end="\r")
        sys.stdout.flush()
        decrypted = decrypt_affine_bigram(ciphertext, a, b)
        if decrypted is None:
            sc = 0.0
            dec = None
        else:
            sc = score_russian_likeness(decrypted)
            dec = decrypted
        candidates_data.append((a,b,sc,dec))
    print(" " * 60, end="\r")

    candidates_data.sort(key=lambda t: t[2], reverse=True)
    best_a, best_b, best_score, best_decrypted = candidates_data[0]

    with open(candidates_out, "a", encoding="utf-8") as cand_f:
        pass_count = 0
        fail_count = 0
        for (a,b,sc,dec) in candidates_data:
            if a == best_a and b == best_b:
                cand_f.write(f"key({a},{b}) - pass\n")
                pass_count += 1
            else:
                cand_f.write(f"key({a},{b}) - fail\n")
                fail_count += 1
        cand_f.write(f"\nSummary: total={len(candidates_data)}, pass={pass_count}, fail={fail_count}\n")

    print(f"\nПравильний (обраний) ключ для розшифровки: key({best_a},{best_b})  score={best_score:.4f}")

    with open(decrypted_out, "a", encoding="utf-8") as dec_f:
        dec_f.write("===== DECRYPTED WITH SELECTED KEY =====\n")
        dec_f.write(f"Key: a={best_a}, b={best_b}\n")
        dec_f.write(f"Score: {best_score:.6f}\n\n")
        if best_decrypted is not None:
            dec_f.write(best_decrypted + "\n")
        else:
            dec_f.write("<no decryption available>\n")
        dec_f.write("\n=======================================\n")

    total_checked = len(candidates_data)
    print(f"Усього унікальних кандидатів: {total_checked}. Кращий ключ записано у '{decrypted_out}', усі кандидати у '{candidates_out}'.")

if __name__ == "__main__":
    in_fname = "10.txt"
    if not os.path.exists(in_fname):
        print(f"Файл '{in_fname}' не знайдено.")
    else:
        with open(in_fname, "r", encoding="utf-8") as f:
            raw = f.read()
        text = clean_text(raw)
        if len(text) < 2:
            print("Після очистки текст дуже короткий або пустий.")
        else:
            attack_affine_bigram_improved(text,
                                          candidates_out="candidates.txt",
                                          decrypted_out="decrypted.txt")
