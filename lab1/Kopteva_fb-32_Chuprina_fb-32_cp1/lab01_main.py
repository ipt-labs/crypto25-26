#!/usr/bin/env python3

import csv
import math
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List

INPUT_FILE = Path("lab1.txt")
OUT_DIR = Path("out")
LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяіїєґ"


def read_text(p: Path) -> str:
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {p}")
    return p.read_bytes().decode("utf-8", "ignore")


def normalize(text: str, with_spaces: bool) -> str:
    s = text.lower()
    if with_spaces:
        s = re.sub(r"\s+", " ", s)
        allowed = LETTERS + " "
    else:
        allowed = LETTERS
    s = re.sub(fr"[^{re.escape(allowed)}]", "", s)
    if with_spaces:
        s = re.sub(r" +", " ", s).strip()
    return s


def entropy(counts: Counter) -> float:
    n = sum(counts.values())
    if n == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def redundancy(h: float, alphabet_size: int) -> float:
    if alphabet_size <= 1:
        return 0.0
    r = 1.0 - h / math.log2(alphabet_size)
    return max(0.0, min(1.0, r))


def save_unigrams(path: Path, counts: Counter) -> None:
    total = sum(counts.values())
    rows = [(k, counts[k], (counts[k] / total if total else 0.0)) for k in counts]
    rows.sort(key=lambda x: (-x[2], x[0]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["char", "count", "freq"])
        for ch, cnt, freq in rows:
            w.writerow([repr(ch).strip("'"), cnt, f"{freq:.10f}"])


def save_matrix(path: Path, freqs: Dict[str, float], alphabet: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + [repr(c).strip("'") for c in alphabet])
        for a in alphabet:
            row = [repr(a).strip("'")]
            for b in alphabet:
                row.append(f"{freqs.get(a + b, 0.0):.10f}")
            w.writerow(row)


def conditional_h2_from_freqs(freqs: Dict[str, float], alphabet: List[str]) -> float:
    px: Dict[str, float] = {a: 0.0 for a in alphabet}
    for a in alphabet:
        s = 0.0
        for b in alphabet:
            s += freqs.get(a + b, 0.0)
        px[a] = s

    h = 0.0
    for a in alphabet:
        pa = px[a]
        if pa <= 0.0:
            continue
        for b in alphabet:
            pxy = freqs.get(a + b, 0.0)
            if pxy <= 0.0:
                continue
            p_y_given_x = pxy / pa
            h -= pxy * math.log2(p_y_given_x)
    return h


def process_variant(raw: str, name: str, with_spaces: bool) -> dict:
    text = normalize(raw, with_spaces)
    if not text:
        alphabet: List[str] = []
    else:
        if with_spaces and " " in text:
            alphabet = [" "] + sorted({c for c in text if c != " "})
        else:
            alphabet = sorted(set(text))

    uni = Counter(text)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_unigrams(OUT_DIR / f"unigrams_{name}.csv", uni)
    h1 = entropy(uni)
    r1 = redundancy(h1, len(alphabet))

    bi_ov = Counter(text[i:i+2] for i in range(len(text) - 1))
    total_ov = sum(bi_ov.values())
    freqs_ov: Dict[str, float] = {k: v / total_ov for k, v in bi_ov.items()} if total_ov else {}
    save_matrix(OUT_DIR / f"bigrams_overlap_matrix_{name}.csv", freqs_ov, alphabet)
    h2_ov_per_char = entropy(bi_ov) / 2.0
    r2_ov = redundancy(h2_ov_per_char, len(alphabet))
    h2_ov_cond = conditional_h2_from_freqs(freqs_ov, alphabet) if total_ov else 0.0
    r2_ov_cond = redundancy(h2_ov_cond, len(alphabet))

    bi_no = Counter(text[i:i+2] for i in range(0, max(0, len(text) - 1), 2))
    total_no = sum(bi_no.values())
    freqs_no: Dict[str, float] = {k: v / total_no for k, v in bi_no.items()} if total_no else {}
    save_matrix(OUT_DIR / f"bigrams_nonoverlap_matrix_{name}.csv", freqs_no, alphabet)
    h2_no_per_char = entropy(bi_no) / 2.0
    r2_no = redundancy(h2_no_per_char, len(alphabet))
    h2_no_cond = conditional_h2_from_freqs(freqs_no, alphabet) if total_no else 0.0
    r2_no_cond = redundancy(h2_no_cond, len(alphabet))

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

        "H2_overlap_cond": f"{h2_ov_cond:.10f}",
        "R2_overlap_cond": f"{r2_ov_cond:.10f}",
        "H2_nonoverlap_cond": f"{h2_no_cond:.10f}",
        "R2_nonoverlap_cond": f"{r2_no_cond:.10f}",
    }


def main():
    raw = read_text(INPUT_FILE)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summaries = []
    for name, s in (("with_spaces", True), ("no_spaces", False)):
        summaries.append(process_variant(raw, name, s))

    if summaries:
        out_csv = OUT_DIR / "entropy_summary.csv"
        keys = list(summaries[0].keys())
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(summaries)
        print(f"[OK] Saved: {out_csv.resolve()}")


if __name__ == "__main__":
    main()
