import argparse
from colorama import Fore, Style
from chardet.universaldetector import UniversalDetector
from tabulate import tabulate
import magic
import math
import pandas as pd
import os

alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"

def print_error(error: str):
    print(Fore.RED + error + Style.RESET_ALL)

def print_table(frame):
    print(Fore.LIGHTCYAN_EX + tabulate(frame, headers='keys', tablefmt="heavy_grid", showindex=True) + Style.RESET_ALL)

def calc_entropy(frequencies:list[float]) -> float:
	entropy = 0
	for frequency in frequencies:
		if frequency > 0:
			entropy -= frequency * math.log2(frequency)
	return entropy	


def monogram_occurences(text:str,include_ws:bool) -> tuple[dict[str, int], int]:
	prev_ch = None
	total = 0
	monograms_count = {c: 0 for c in alphabet + (" " if include_ws else "")}
	for ch in text:
		temp_ch = ch
		if ch not in alphabet:
			if not include_ws or prev_ch == " ":
				continue
			temp_ch = " "
		monograms_count[temp_ch] += 1
		total += 1
		prev_ch = temp_ch
	return (monograms_count, total)


def bigram_occurences(text:str,include_ws:bool, overlapped: bool) -> tuple[dict[str, int], int]:
	temp_alphabet = alphabet + (" " if include_ws else "")
	bigram_count = {c1+c2:0 for c1 in temp_alphabet for c2 in temp_alphabet}
	# TODO think about what to do with double ws
	# if include_ws:
	# 	del bigram_count["  "]
	total = 0
	prev_ch = None
	index = 0
	for ch in text:
		temp_ch = ch
		if ch not in alphabet:
			if not include_ws or prev_ch == " ":
				continue
			temp_ch = " "	
		if prev_ch is not None and (overlapped or index % 2 == 1):
			bigram_count[prev_ch+temp_ch] += 1
			total += 1
		prev_ch = temp_ch
		index += 1
	return (bigram_count, total)


def bigram_stat_dict_to_dataframe(bigram_count: dict[str,int]) -> pd.DataFrame:
    letters = sorted({letter for bigram in bigram_count.keys() for letter in bigram})
    data = {c1: [bigram_count[c1+c2] for c2 in letters] for c1 in letters}
    df = pd.DataFrame(data, index=letters)
    return df.T

def process_text(text:str):
	print(f"{Fore.LIGHTGREEN_EX}Text length:{Fore.LIGHTBLUE_EX} {len(text)}{Style.RESET_ALL}")
	filtered_text = text.strip().lower().replace("ё","е").replace("ъ","ь")

	(monogram_occurences_without_ws, monogram_total) = monogram_occurences(filtered_text, False)
	(monogram_occurences_ws, monogram_total_ws) = monogram_occurences(filtered_text, True)

	(not_overlapped_bigrams_occurences, not_overlapped_bigrams_total) = bigram_occurences(filtered_text, False, False)
	(not_overlapped_bigrams_occurences_ws, not_overlapped_bigrams_total_ws) = bigram_occurences(filtered_text, True, False)

	(overlapping_bigrams_occurences, overlapping_bigrams_total) = bigram_occurences(filtered_text, False, True)
	(overlapping_bigrams_occurences_ws, overlapping_bigrams_total_ws) = bigram_occurences(filtered_text, True, True)

	print_table(bigram_stat_dict_to_dataframe(not_overlapped_bigrams_occurences))
	print_table(bigram_stat_dict_to_dataframe(not_overlapped_bigrams_occurences_ws))
	
	

if __name__ == "__main__":
	description = Fore.LIGHTBLUE_EX + r"""
   _____         _      _                _                    
  |_   _|____  _| |_   / \   _ __   __ _| |_   _ _______ _ __ 
    | |/ _ \ \/ / __| / _ \ | '_ \ / _` | | | | |_  / _ \ '__|
    | |  __/>  <| |_ / ___ \| | | | (_| | | |_| |/ /  __/ |   
    |_|\___/_/\_\\__/_/   \_\_| |_|\__,_|_|\__, /___\___|_|   
                                            |___/              
        """ + Style.RESET_ALL
	parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("-f",dest="file",type=str, required=True, help="File to analyze")
	args = parser.parse_args()
	print(description)
	file_path = args.file
	if not os.path.exists(file_path):
		print_error(f"{file_path} does not exists")
	else:
		print(Fore.LIGHTGREEN_EX + 35*"==" + "\n" + 35*"==" + Style.RESET_ALL)
		file_type = magic.from_file(args.file,mime=True)
		print(f"{Fore.LIGHTGREEN_EX}File type of {file_path}:{Fore.LIGHTBLUE_EX} {file_type}{Style.RESET_ALL}")
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
				print(f"{Fore.LIGHTGREEN_EX}Encoding detection result:{Fore.LIGHTBLUE_EX} {detection_result}{Style.RESET_ALL}")
				with open(file_path, encoding=detector.result['encoding']) as f:
					content = f.read()
					process_text(content)
			else:
				print_error("Failed to detect encoding")	
		
