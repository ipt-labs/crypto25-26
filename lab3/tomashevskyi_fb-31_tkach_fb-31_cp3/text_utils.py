# -*- coding: utf-8 -*-
import json, csv
from pathlib import Path
from collections import Counter

RU_LETTERS = "абвгдежзийклмнопрстуфхцчшщьыэюя"
N = len(RU_LETTERS)
VOWELS = set("аеёиоуыэюя".replace("ё", "е"))

def build_maps():
    c2i = {ch: i for i, ch in enumerate(RU_LETTERS)}
    i2c = {i: ch for ch, i in c2i.items()}
    return c2i, i2c

C2I, I2C = build_maps()

def normalize(txt: str) -> str:
    txt = txt.lower().replace("ё", "е").replace("ъ", "ь")
    return "".join(ch for ch in txt if ch in C2I)

def non_overlap_pairs(txt: str):
    L = len(txt) // 2 * 2
    return [txt[i:i+2] for i in range(0, L, 2)]

def overlap_pairs(txt: str):
    return [txt[i:i+2] for i in range(len(txt) - 1)]

def bigram_to_int(bg: str, n=N):
    return C2I[bg[0]] * n + C2I[bg[1]]

def int_to_bigram(x: int, n=N):
    return I2C[(x // n) % n] + I2C[x % n]

def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def save_text(path: Path, txt: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt, encoding="utf-8")

def write_bigram_csv(path: Path, data):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["pair", "count", "freq"])
        writer.writeheader()
        writer.writerows(data)
