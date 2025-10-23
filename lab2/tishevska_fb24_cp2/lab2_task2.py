# -*- coding: utf-8 -*-
from pathlib import Path
from collections import Counter
import argparse
import csv
import sys

import matplotlib.pyplot as plt

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def normalize(text: str) -> str:
    t = text.lower().replace("ё", "е")
    return "".join(ch for ch in t if ch in ALPHABET)

def index_of_coincidence(text: str) -> float:
    y = normalize(text)
    n = len(y)
    if n < 2:
        return 0.0
    freq = Counter(y)
    s = sum(v * (v - 1) for v in freq.values())
    return s / (n * (n - 1))

def main():
    ap = argparse.ArgumentParser(
        description="IC для normalized_task1.txt та всіх довжина*.txt + діаграма."
    )
    ap.add_argument(
        "--indir",
        default="результати_завдання_1",
        help="Каталог з normalized_task1.txt і довжина*.txt",
    )
    ap.add_argument(
        "--outcsv",
        default="результати_task2.csv",
        help="CSV з результатами",
    )
    ap.add_argument(
        "--plot",
        default="diagram_task2.png",
        help="Ім'я файлу для збереження діаграми (PNG).",
    )
    ap.add_argument(
        "--show",
        action="store_true",
        help="Показати діаграму у вікні після побудови.",
    )
    args = ap.parse_args()

    indir = Path(args.indir)
    if not indir.exists():
        print(f"Каталог не знайдено: {indir}", file=sys.stderr)
        sys.exit(1)

    files = []
    pt_file = indir / "normalized_task1.txt"
    if pt_file.exists():
        files.append(pt_file)
    files.extend(sorted(indir.glob("довжина*.txt")))

    if not files:
        print("Не знайдено normalized_task1.txt або довжина*.txt", file=sys.stderr)
        sys.exit(1)

    rows = []
    for f in files:
        txt = f.read_text(encoding="utf-8")
        ic = index_of_coincidence(txt)
        rows.append({"file": f.name, "chars": len(normalize(txt)), "IC": ic})

    with open(args.outcsv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "chars", "IC"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    pt_row = next((r for r in rows if r["file"] == "normalized_task1.txt"), None)
    print("\nІндекси відповідності (IC):")
    print("-" * 60)
    if pt_row:
        print(f"{'OPEN TEXT':<30} n={pt_row['chars']:<7} IC={pt_row['IC']:.6f}")
        print("-" * 60)
    for r in sorted((x for x in rows if x is not pt_row), key=lambda z: z["IC"], reverse=True):
        print(f"{r['file']:<30} n={r['chars']:<7} IC={r['IC']:.6f}")
    print("-" * 60)
    print(f"CSV збережено у: {Path(args.outcsv).resolve()}")

    labels = []
    values = []
    for r in rows:
        if r["file"] == "normalized_task1.txt":
            labels.append("OPEN_TEXT")
        else:
            name = r["file"].replace("довжина", "r=").replace(".txt", "")
            labels.append(name)
        values.append(r["IC"])

    plt.figure(figsize=(10, 5))
    bars = plt.bar(labels, values)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Index of Coincidence (IC)")
    plt.title("IC для відкритого тексту та шифртекстів (Віженер)")

    for b, v in zip(bars, values):
        plt.text(b.get_x() + b.get_width()/2.0, b.get_height(), f"{v:.4f}",
                 ha="center", va="bottom", fontsize=9)

    plt.tight_layout()

    if args.plot:
        out_png = Path(args.plot)
        plt.savefig(out_png, dpi=150)
        print(f"Діаграму збережено у: {out_png.resolve()}")
    if args.show:
        plt.show()
    plt.close()

if __name__ == "__main__":
    main()
