# -*- coding: utf-8 -*-
import math
from text_utils import bigram_to_int, int_to_bigram, non_overlap_pairs, N

MOD = N * N  # 961

def gcd_ext(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = gcd_ext(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def inv_mod(a, m):
    a %= m
    g, x, y = gcd_ext(a, m)
    if g != 1:
        raise ValueError("no inverse")
    return x % m

def solve_congruence(a, b, mod):
    a %= mod; b %= mod
    g = math.gcd(a, mod)
    if b % g != 0:
        return []
    A1, B1, M1 = a // g, b // g, mod // g
    inv = inv_mod(A1, M1)
    base = (inv * B1) % M1
    return [(base + k*M1) % mod for k in range(g)]

def decrypt(txt: str, a: int, b: int) -> str:
    inva = inv_mod(a, MOD)
    res = []
    for bg in non_overlap_pairs(txt):
        y = bigram_to_int(bg)
        x = (inva * (y - b)) % MOD
        res.append(int_to_bigram(x))
    return "".join(res)
