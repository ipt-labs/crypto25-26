import argparse
import itertools
import os
from chardet import UniversalDetector
import magic
import pandas as pd
from helpers.styles import print_error, print_green_blue_colored_pair, print_df
from helpers.modular_arithmetic import modular_linear_equation, gcd
from helpers.text_stats import *
from bigram_affine_cipher import BigramAffineCipher
from colorama import Fore, Style

# this alphabet is for decrypting files in "variants" folder
# to decrypt file in "for_test" use абвгдежзийклмнопрстуфхцчшщыьэюя
alphabet = "абвгдежзийклмнопрстуфхцчшщьыэюя"
#alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"

alphabet_len = len(alphabet)
modulus = alphabet_len ** 2
most_common_bigrams = ["ст",  "но",  "то",  "на",  "ен"]

def process_text(content:str, save_basepath: str, encoding: str) -> None:
    text_stats_calc = TextStats(alphabet)
    affine_bg_cipher = BigramAffineCipher(alphabet)

    content = ''.join(ch for ch in content.lower() if ch in alphabet)

    bigr_frequencies = text_stats_calc.bigram_frequencies(content)
    bigrs_sorted = sorted(bigr_frequencies, key=bigr_frequencies.get, reverse=True)
    most_common_bigrams_in_ct = []
    for i in range(len(bigrs_sorted)):
        if i < 5 or bigrs_sorted[i-1] == bigrs_sorted[i]:
            most_common_bigrams_in_ct.append(bigrs_sorted[i])
        else:
            break
    print(Fore.LIGHTGREEN_EX + "The most common bigrams in ct:" + Style.RESET_ALL)
    print_df(pd.DataFrame([bigr_frequencies[k] for k in most_common_bigrams_in_ct], index=most_common_bigrams_in_ct).T)

    processed = set()

    for (i, j) in itertools.product(range(len(most_common_bigrams)), range(len(most_common_bigrams_in_ct))):
        x_1 = affine_bg_cipher.bigram_to_int(most_common_bigrams[i])
        y_1 = affine_bg_cipher.bigram_to_int(most_common_bigrams_in_ct[j])
        
        for (k, l) in itertools.product(range(len(most_common_bigrams)), range(len(most_common_bigrams_in_ct))):
            if i==k or j==l:
                continue
            
            x_2 = affine_bg_cipher.bigram_to_int(most_common_bigrams[k])
            y_2 = affine_bg_cipher.bigram_to_int(most_common_bigrams_in_ct[l])
            
            solutions = modular_linear_equation(x_1 - x_2, y_1 - y_2, modulus)

            for a in solutions:
                b = (y_1 - a * x_1) % modulus
                if (a,b)in processed:
                    continue
                processed.add((a,b))

                if gcd(a,modulus) != 1:
                    continue

                pt = affine_bg_cipher.decrypt(content, a, b)

                pt_monogram_entr = text_stats_calc.calc_entropy(text_stats_calc.monogram_frequencies(pt))
                pt_bigram_entr = text_stats_calc.calc_entropy(text_stats_calc.bigram_frequencies(pt,overlapped=True))
                if pt_monogram_entr < 4.455 or pt_bigram_entr<4.125:
                    print(Fore.LIGHTGREEN_EX + 35*"==" + Style.RESET_ALL)
                    print_green_blue_colored_pair("Key:", f"({a},{b})")
                    print_green_blue_colored_pair("PT H1:",pt_monogram_entr)
                    print_green_blue_colored_pair("PT H2 (overlapped):",pt_bigram_entr)
                    print_green_blue_colored_pair("Decryption result:", f"\n{pt}")
                    dec_file = f"{save_basepath}_dec_{a}_{b}.txt"
                    with open(dec_file, "w", encoding=encoding) as f:
                        f.write(pt)
                        print_green_blue_colored_pair("Saved to:", dec_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f",dest="file",type=str, required=True, help="File to decrypt")
    args = parser.parse_args()

    dec_dir = "decrypted"
    os.makedirs(dec_dir,exist_ok=True)

    file_path = args.file
    if file_path:
        print(Fore.LIGHTGREEN_EX + 35*"==" + "\n" + 35*"==" + Style.RESET_ALL)
        if not os.path.exists(file_path):
            print_error(f"{file_path} does not exists")
        else:
            if os.path.isdir(file_path):
                print_error(f"{file_path} is dir")
            else:
                file_type = magic.from_file(file_path,mime=True)
                print_green_blue_colored_pair(f"File type of {file_path}:", file_type)
                if "text" not in file_type:
                    print_error("Please, provide text file")
                else:   
                    detector = UniversalDetector()
                    with open(file_path, 'rb') as f:
                        for line in f.readlines():
                            detector.feed(line)
                            if detector.done: break
                        detector.close()
                    detection_result = detector.result
                    if detection_result and detection_result["confidence"] > 0.8:
                        print_green_blue_colored_pair("Encoding detection result:", detection_result)
                        with open(file_path, encoding=detector.result['encoding']) as f:
                            process_text(f.read(), os.path.join(dec_dir,os.path.basename(file_path).split('.')[0]), detector.result['encoding'])
                    else:
                        print_error("Failed to detect encoding")