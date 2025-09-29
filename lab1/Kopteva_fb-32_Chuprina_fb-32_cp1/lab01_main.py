#!/usr/bin/env python3

import csv, math, re
from pathlib import Path
from collections import Counter

INPUT_FILE = Path("data/input.txt")
OUT_DIR = Path("out")
LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяіїєґ"

def read_text(p: Path) -> str:
    return p.read_bytes().decode("utf-8", "ignore")

def normalize(text: str, with_spaces: bool) -> str:
    s = text.lower()
    allowed = LETTERS + (r"\s" if with_spaces else "")
    s = re.sub(f"[^{allowed}]", " " if with_spaces else "", s, flags=re.IGNORECASE)
    return " ".join(s.split()) if with_spaces else s

def entropy(counts: Counter) -> float:
    n = sum(counts.values())
    return 0.0 if n == 0 else -sum((c/n)*math.log2(c/n) for c in counts.values() if c)

def redundancy(h: float, alphabet_size: int) -> float:
    return 0.0 if alphabet_size <= 1 else max(0.0, min(1.0, 1 - h / math.log2(alphabet_size)))

def save_unigrams(path: Path, counts: Counter):
    total = sum(counts.values())
    rows = [(k, counts[k], (counts[k]/total if total else 0.0)) for k in counts]
    rows.sort(key=lambda x: (-x[2], x[0]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["char", "count", "freq"])
        for ch, cnt, freq in rows:
            w.writerow([repr(ch).strip("'"), cnt, f"{freq:.10f}"])

def save_matrix(path: Path, freqs: dict[str, float], alphabet: list[str]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + [repr(c).strip("'") for c in alphabet])
        for a in alphabet:
            w.writerow([repr(a).strip("'")] + [f"{freqs.get(a+b, 0.0):.10f}" for b in alphabet])

def process_variant(raw: str, name: str, with_spaces: bool) -> dict:
    text = normalize(raw, with_spaces)
    alphabet = ([" "] + sorted({c for c in text if c != " "})) if (with_spaces and " " in text) else sorted(set(text))

    uni = Counter(text)
    save_unigrams(OUT_DIR / f"unigrams_{name}.csv", uni)
    h1 = entropy(uni)
    r1 = redundancy(h1, len(alphabet))

    bi_ov = Counter(text[i:i+2] for i in range(len(text)-1))
    total_ov = sum(bi_ov.values())
    freqs_ov = {k: v/total_ov for k, v in bi_ov.items()} if total_ov else {}
    save_matrix(OUT_DIR / f"bigrams_overlap_matrix_{name}.csv", freqs_ov, alphabet)
    h2_ov_per_char = (entropy(bi_ov) / 2.0)
    r2_ov = redundancy(h2_ov_per_char, len(alphabet))

    bi_no = Counter(text[i:i+2] for i in range(0, len(text)-1, 2))
    total_no = sum(bi_no.values())
    freqs_no = {k: v/total_no for k, v in bi_no.items()} if total_no else {}
    save_matrix(OUT_DIR / f"bigrams_nonoverlap_matrix_{name}.csv", freqs_no, alphabet)
    h2_no_per_char = (entropy(bi_no) / 2.0)
    r2_no = redundancy(h2_no_per_char, len(alphabet))

    return {
        "variant": name,
        "with_spaces": with_spaces,
        "chars": len(text),
        "alphabet_size": len(alphabet),
        "H1": f"{h1:.10f}",
        "R1": f"{r1:.10f}",
        "H2_overlap_per_char": f"{h2_ov_per_char:.10f}",
        "R2_overlap": f"{r2_ov:.10f}",
        "H2_nonoverlap_per_char": f"{h2_no_per_char:.10f}",
        "R2_nonoverlap": f"{r2_no:.10f}",
    }

def main():
    raw = read_text(INPUT_FILE)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []
    for name, s in (("with_spaces", True), ("no_spaces", False)):
        summaries.append(process_variant(raw, name, s))
    if summaries:
        with open(OUT_DIR / "entropy_summary.csv", "w", newline="", encoding="utf-8") as f:
            keys = list(summaries[0].keys())
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(summaries)

if __name__ == "__main__":
    main()
