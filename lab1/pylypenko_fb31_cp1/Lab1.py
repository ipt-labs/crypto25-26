import math
import pandas as pd
from collections import Counter

ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
VALID_CHARS = set(ALPHABET + ' ')

def text_preprocessor(raw_text, keep_spaces=False):
    raw_text = raw_text.lower()
    filtered = [char for char in raw_text if char in VALID_CHARS]
    text_str = "".join(filtered)
    
    if keep_spaces:
        return " ".join(text_str.split())
    else:
        return text_str.replace(" ", "")

def get_shannon_entropy(freq_map):
    ent = 0.0
    for p in freq_map.values():
        if p > 0:
            ent -= p * math.log2(p)
    return ent

def get_redundancy(h_val, alphabet_size):
    if alphabet_size <= 1: 
        return 0.0
    h_max = math.log2(alphabet_size)
    return 1.0 - (h_val / h_max)

def compute_frequencies(sequence):
    cnt = Counter(sequence)
    total = sum(cnt.values())
    return {k: v / total for k, v in cnt.items()}

def generate_bigrams(text, overlap=True):
    if overlap:
        return [a + b for a, b in zip(text, text[1:])]
    else:
        return [a + b for a, b in zip(text[::2], text[1::2])]

def process_scenario(text_content, with_spaces):
    clean_txt = text_preprocessor(text_content, keep_spaces=with_spaces)
    alphabet_len = 34 if with_spaces else 33 

    freq_letters = compute_frequencies(clean_txt)
    h1 = get_shannon_entropy(freq_letters)
    r1 = get_redundancy(h1, alphabet_len)

    bg_ov = generate_bigrams(clean_txt, overlap=True)
    freq_bg_ov = compute_frequencies(bg_ov)
    h2_ov = get_shannon_entropy(freq_bg_ov) / 2
    r2_ov = get_redundancy(h2_ov, alphabet_len)

    bg_no = generate_bigrams(clean_txt, overlap=False)
    freq_bg_no = compute_frequencies(bg_no)
    h2_no = get_shannon_entropy(freq_bg_no) / 2
    r2_no = get_redundancy(h2_no, alphabet_len)

    return {
        "data": {
            "letters": freq_letters,
            "bg_ov": freq_bg_ov,
            "bg_no": freq_bg_no
        },
        "stats": {
            "H1": h1, 
            "R1": r1,
            "H2 (з перетином)": h2_ov, 
            "R2 (з перетином)": r2_ov,
            "H2 (без перетину)": h2_no, 
            "R2 (без перетину)": r2_no
        }
    }

def format_matrix(freq_dict):
    chars = sorted(list(set([k[0] for k in freq_dict.keys()] + [k[1] for k in freq_dict.keys()])))
    df = pd.DataFrame(0.0, index=chars, columns=chars)
    
    for bigram, p in freq_dict.items():
        try:
            df.at[bigram[0], bigram[1]] = p
        except KeyError:
            continue
        
    return df

def save_report_ukr(fname, res_space, res_nospace):
    sheet_names = [
        "Підсумки",
        "Літери з проб.", "Літери без проб.",
        "Біграми з проб. перет.", "Біграми з проб. без перет.",
        "Біграми без проб. перет", "Біграми без проб. без перет."
    ]
    
    with pd.ExcelWriter(fname) as writer:
        summary_dict = {
            "Показник": [
                "H1", "R1 (надлишковість)", 
                "H2 (з перетином)", "R2 (з перетином)", 
                "H2 (без перетину)", "R2 (без перетину)"
            ],
            "З пробілами": list(res_space["stats"].values()),
            "Без пробілів": list(res_nospace["stats"].values())
        }
        pd.DataFrame(summary_dict).to_excel(writer, sheet_name=sheet_names[0], index=False)

        pd.Series(res_space["data"]["letters"], name="Частота").sort_values(ascending=False).to_excel(writer, sheet_name=sheet_names[1])
        pd.Series(res_nospace["data"]["letters"], name="Частота").sort_values(ascending=False).to_excel(writer, sheet_name=sheet_names[2])

        format_matrix(res_space["data"]["bg_ov"]).to_excel(writer, sheet_name=sheet_names[3])
        format_matrix(res_space["data"]["bg_no"]).to_excel(writer, sheet_name=sheet_names[4])
        format_matrix(res_nospace["data"]["bg_ov"]).to_excel(writer, sheet_name=sheet_names[5])
        format_matrix(res_nospace["data"]["bg_no"]).to_excel(writer, sheet_name=sheet_names[6])
        
    return len(sheet_names)

if __name__ == "__main__":
    input_filename = "Master_i_Margarita.txt"
    output_filename = "Lab1_Results.xlsx"

    try:
        with open(input_filename, encoding="utf-8") as f:
            full_text = f.read()
            
        results_with_space = process_scenario(full_text, with_spaces=True)
        results_no_space = process_scenario(full_text, with_spaces=False)

        print("\n результати з пробілами")
        for key, val in results_with_space["stats"].items():
            print(f"{key:25}: {val:.5f}")

        print("\n результати без пробілів")
        for key, val in results_no_space["stats"].items():
            print(f"{key:25}: {val:.5f}")
        
        sheets_count = save_report_ukr(output_filename, results_with_space, results_no_space)
        print(f"\nФайл '{output_filename}' збережено. Кількість аркушів: {sheets_count}")
        
    except FileNotFoundError:
        print(f"Помилка: Не знайдено файл '{input_filename}'.")