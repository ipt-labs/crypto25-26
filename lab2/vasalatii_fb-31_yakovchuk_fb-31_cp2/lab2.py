import argparse
from random import choice
from colorama import Fore, Style
from chardet.universaldetector import UniversalDetector
import magic
import os
import pandas as pd
from tabulate import tabulate

class VigenereCipher:
    def __init__(self, key: str, alphabet: str):
        if not alphabet:
            raise ValueError("alphabet cannot be empty")
        elif not key:
            raise ValueError("key cannot be empty")
        self.alphabet = "".join(dict.fromkeys(alphabet))
        for key_ch in key:
            if key_ch not in self.alphabet:
                raise ValueError("key cannot contain characters that are not in alphabet")
        self.alphabet_len = len(self.alphabet)
        self.key = key
        self.key_len = len(key)
        self.char_to_idx = {ch: i for i, ch in enumerate(self.alphabet)}

    def encrypt(self, pt: str) -> str:
        ct = ""
        for i, ch in enumerate(pt):
            if ch in self.alphabet:
                ct += self.alphabet[
                    (self.char_to_idx[ch] + self.char_to_idx[self.key[i%self.key_len]]) % self.alphabet_len
                ]
        return ct

    def decrypt(self, ct: str) -> str:
        pt = ""
        for i, ch in enumerate(ct):
            if ch in self.alphabet:
                pt += self.alphabet[
                    (self.char_to_idx[ch] - self.char_to_idx[self.key[i%self.key_len]]) % self.alphabet_len
                ]
        return pt


def print_error(error: str) -> None:
	print(Fore.RED + error + Style.RESET_ALL)

def print_green_blue_colored_pair(tag: str, value: str | int | float | dict, indentation: str='') -> None:
	print(indentation + Fore.LIGHTGREEN_EX + tag + " " + Fore.LIGHTBLUE_EX + str(value) + Style.RESET_ALL)

def print_df(frame: pd.DataFrame, title: str=None) -> None:
	table_str = tabulate(frame, headers='keys', tablefmt="heavy_grid", showindex=False)
	table_width = max(len(line) for line in table_str.splitlines())

	if title:
		print(Fore.LIGHTGREEN_EX + title.center(table_width) + Style.RESET_ALL)

	print(Fore.LIGHTCYAN_EX + table_str + Style.RESET_ALL)

def calculate_ic(text:str):
    total = 0
    symbol_count = {}
    for ch in text:
        total+=1
        if ch in symbol_count:
            symbol_count[ch] +=1 
        else:
            symbol_count[ch] = 1
    return sum([count*(count-1) for count in list(symbol_count.values())])/(total*(total-1))


# def calc_match_statistics(text:str,r: str):
#     d_r = 0
#     for i in range(len(text)-r):
#         if text[i] == text[i+r]:
#             d_r += 1
#     return d_r

def gen_rand_word(alphabet:str,size:int):
     return "".join(choice(alphabet) for _ in range(size))

def process_text(content:str):
    alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"
    filtered_text = ''.join(filter(lambda char: char in alphabet,content.strip().lower().replace("ё","е").replace("ъ","ь")))

    keys = [gen_rand_word(alphabet, i) for i in range(2, 6)]
    keys.extend(gen_rand_word(alphabet, i) for i in range(10, 21))
    print_green_blue_colored_pair("Used random keys:",keys)
    cts = {}
    stats = []

    for key in keys:
        ct = VigenereCipher(key, alphabet).encrypt(filtered_text)
        cts[key] = ct
        stats.append({
             'key_len': len(key),'ic': calculate_ic(ct)
            #  ,'match_stat': calc_match_statistics(ct, len(key))
             })

    df = pd.DataFrame(stats)
    print_df(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f",dest="files",type=str, required=True, nargs="+", help="File to analyze")
    args = parser.parse_args()

    for file_path in args.files:
        print(Fore.LIGHTGREEN_EX + 35*"==" + "\n" + 35*"==" + Style.RESET_ALL)
        if not os.path.exists(file_path):
             print_error(f"{file_path} does not exists")
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
                if detection_result:
                    print_green_blue_colored_pair("Encoding detection result:", detection_result)
                    with open(file_path, encoding=detector.result['encoding']) as f:
                        content = f.read()
                        process_text(content)
                else:
                    print_error("Failed to detect encoding")