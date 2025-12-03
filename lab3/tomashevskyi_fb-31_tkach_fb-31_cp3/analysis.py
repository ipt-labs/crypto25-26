# -*- coding: utf-8 -*-
import math
from collections import Counter
from itertools import permutations
from text_utils import overlap_pairs, bigram_to_int, N
from cipher_math import solve_congruence, MOD

REF_BIGRAMS = ["ст","но","то","на","ен"]
BAD_BIGRAMS = {
    "аь","оь","уь","эь","ыь","йь","ьь","ыы","йй","ьй","йы","ьы",
    "жы","шы","ыа","ыо","ыу","ые","яы","юы","эы","ьи","ые","ьь"
}
BIGRAM_CHECK_LIST = ["ст","но","то","на","ен","ра","ко","ни","во","ро"]
RARE = set("щфь")
LETTER_FREQ = {
    "о":0.10,"е":0.085,"а":0.08,"и":0.073,"н":0.067,"т":0.063,
    "с":0.055,"р":0.047,"в":0.045,"л":0.044,"к":0.034,"м":0.032
}
VOWELS = set("аеёиоуыэюя".replace("ё", "е"))

def coincidence_index(txt: str) -> float:
    n = len(txt)
    if n < 2: return 0
    freq = Counter(txt)
    return sum(v*(v-1) for v in freq.values()) / (n*(n-1))

def evaluate_plaintext(txt: str) -> dict:
    n = len(txt)
    if not n:
        return {"score": -999999}
    count = Counter(txt)
    vowel_ratio = sum(count.get(ch,0) for ch in VOWELS) / n
    rare_part = sum(count.get(ch,0)/n for ch in RARE)
    top_sum = sum(count.get(ch,0)/n for ch in LETTER_FREQ)
    forb = overlap_pairs(txt)
    bad_ratio = sum(1 for bg in forb if bg in BAD_BIGRAMS) / max(1, len(forb))
    common_bi = Counter(forb)
    bi_part = sum(common_bi.get(bg, 0) for bg in BIGRAM_CHECK_LIST) / max(1, len(common_bi))
    ic = coincidence_index(txt)

    score = 40*top_sum - 300*bad_ratio + 180*bi_part
    if vowel_ratio < 0.32 or vowel_ratio > 0.62:
        score -= 60 * abs(vowel_ratio - 0.47)
    score -= 1000 * abs(ic - 0.055)
    score -= 100 * rare_part

    return dict(score=score, vowels=vowel_ratio, rare=rare_part, IC=ic)

def generate_keys(cipher_top, ref_top=REF_BIGRAMS):
    variants = set()
    full_log = []
    for p1, p2 in permutations(ref_top, 2):
        X1, X2 = bigram_to_int(p1), bigram_to_int(p2)
        dx = (X1 - X2) % MOD
        for c1, c2 in permutations(cipher_top, 2):
            Y1, Y2 = bigram_to_int(c1), bigram_to_int(c2)
            dy = (Y1 - Y2) % MOD
            for a in solve_congruence(dx, dy, MOD):
                if math.gcd(a, MOD) != 1:
                    continue
                b = (Y1 - a * X1) % MOD
                variants.add((a, b))
                full_log.append({"pair": f"{p1}->{c1}, {p2}->{c2}", "a": a, "b": b})
    return sorted(variants), full_log
