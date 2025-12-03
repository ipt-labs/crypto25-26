# -*- coding: utf-8 -*-
from pathlib import Path
from collections import Counter

from text_utils import (
    normalize, non_overlap_pairs, save_json, save_text, write_bigram_csv
)
from cipher_math import decrypt
from analysis import generate_keys, evaluate_plaintext

# === Шляхи ===
BASE_DIR = Path(".")
RESULTS = Path("result_data")
RESULTS.mkdir(exist_ok=True)

def process_file(input_path: Path):
    name = input_path.stem
    raw = input_path.read_text(encoding="utf-8", errors="ignore")
    cleaned = normalize(raw)
    (RESULTS / f"{name}_normalized.txt").write_text(cleaned, encoding="utf-8")

    bigrams = Counter(non_overlap_pairs(cleaned))
    total = sum(bigrams.values())
    rows = [{"pair": bg, "count": c, "freq": c/total} for bg, c in bigrams.most_common()]
    write_bigram_csv(RESULTS / f"{name}_bigrams.csv", rows)

    cipher_top = [r["pair"] for r in rows[:5]]
    save_json(RESULTS / f"{name}_top_cipher_bigrams.json", cipher_top)

    keys, details = generate_keys(cipher_top)
    save_json(RESULTS / f"{name}_key_candidates.json", details)

    all_scores = []
    out_dec = RESULTS / f"{name}_decrypted_variants"
    out_dec.mkdir(parents=True, exist_ok=True)

    for a, b in keys:
        try:
            text_dec = decrypt(cleaned, a, b)
        except Exception:
            continue
        info = evaluate_plaintext(text_dec)
        path_dec = out_dec / f"{a}_{b}.txt"
        path_dec.write_text(text_dec, encoding="utf-8")
        all_scores.append({"a": a, "b": b, **info, "path": str(path_dec)})

    all_scores.sort(key=lambda x: x["score"], reverse=True)
    save_json(RESULTS / f"{name}_scored_variants.json", all_scores[:40])

    if all_scores:
        best = all_scores[0]
        save_text(RESULTS / f"{name}_top_result.txt",
                  f"Best a={best['a']}, b={best['b']}\n{best}")
        save_text(RESULTS / f"{name}_decrypted.txt",
                  Path(best["path"]).read_text(encoding='utf-8'))


if __name__ == "__main__":
    for file in BASE_DIR.glob("sh.txt"):
        process_file(file)
