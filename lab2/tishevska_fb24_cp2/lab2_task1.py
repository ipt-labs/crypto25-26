# -*- coding: utf-8 -*-
from pathlib import Path
from collections import Counter

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)
a2i = {ch: i for i, ch in enumerate(ALPHABET)}
i2a = {i: ch for i, ch in enumerate(ALPHABET)}

def normalize(text: str) -> str:
    t = text.lower().replace("ё", "е")
    return "".join(ch for ch in t if ch in ALPHABET)

def key_ok(key: str) -> str:
    k = normalize(key)
    if not k:
        raise ValueError("Ключ порожній після нормалізації.")
    return k

def vig_encrypt(plaintext: str, key: str) -> str:
    p = normalize(plaintext)
    k = key_ok(key)
    res = []
    r = len(k)
    for i, ch in enumerate(p):
        x = a2i[ch]
        ki = a2i[k[i % r]]
        y = (x + ki) % M
        res.append(i2a[y])
    return "".join(res)

def main():
    PLAINTEXT_FILE = "text_task1.txt"

    KEYS = [
        "ши",
        "код",
        "тест",
        "ключи",
        "математика",
        "криптоанализ",
        "частотныйанализ",
        "безопасностьданных",
    ]

    OUTDIR = Path("результати_завдання_1")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    raw = Path(PLAINTEXT_FILE).read_text(encoding="utf-8")
    pt = normalize(raw)

    if len(pt) > 2800:
        pt = pt[:2800]

    (OUTDIR / "normalized_task1.txt").write_text(pt, encoding="utf-8")

    for key in KEYS:
        k = key_ok(key)
        ct = vig_encrypt(pt, k)
        fname = f"довжина{len(k)}_{k}.txt"
        (OUTDIR / fname).write_text(ct, encoding="utf-8")

    print(f"Готово. Файли в: {OUTDIR.resolve()}")
    print("Згенеровано шифртексти для ключів:", ", ".join(f"{k} (r={len(k)})" for k in KEYS))

if __name__ == "__main__":
    main()
