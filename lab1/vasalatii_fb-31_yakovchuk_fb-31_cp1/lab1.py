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


def print_df(frame, title=None):
    table_str = tabulate(frame, headers='keys', tablefmt="heavy_grid", showindex=True)
    table_width = max(len(line) for line in table_str.splitlines())

    if title:
        print(Fore.LIGHTGREEN_EX + title.center(table_width) + Style.RESET_ALL)

    print(Fore.LIGHTCYAN_EX + table_str + Style.RESET_ALL)


def print_green_blue_colored_pair(tag, value, indentation=''):
    print(indentation + Fore.LIGHTGREEN_EX + tag + " " + Fore.LIGHTBLUE_EX + str(value) + Style.RESET_ALL)

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


def calculate_ngram_frequencies(ngrams_count: dict[str, int], ngrams_total: int) -> dict[str, float]:
	frequencies = ngrams_count.copy()
	for ngram in ngrams_count:
		frequencies[ngram] /= ngrams_total 
	return frequencies


def calc_entropy(frequencies:dict[str, float]) -> float:
	entropy = 0
	for bigram in frequencies:
		frequency = frequencies[bigram]
		if frequency > 0:
			entropy -= frequency * math.log2(frequency)
	return entropy	


def bigram_stat_dict_to_dataframe(bigram_count: dict[str,int]) -> pd.DataFrame:
    letters = sorted({letter for bigram in bigram_count.keys() for letter in bigram})
    data = {c1: [bigram_count[c1+c2] for c2 in letters] for c1 in letters}
    df = pd.DataFrame(data, index=letters)
    return df.T


def process_text(text:str):
	print_green_blue_colored_pair("Text length:", len(text))

	# prepare text
	filtered_text = text.strip().lower().replace("ё","е").replace("ъ","ь")

	# ngram counts and frequencies will be saved in different sheets of xlsx file
	writer = pd.ExcelWriter('lab_results.xlsx',engine='xlsxwriter')   

	# count monograms
	(monogram_occurences_without_ws, monogram_total) = monogram_occurences(filtered_text, False)
	pd.DataFrame(monogram_occurences_without_ws.items(),columns=["Monogram","Count"], index=None).to_excel(writer, sheet_name="CO_MG", index=False)
	(monogram_occurences_ws, monogram_total_ws) = monogram_occurences(filtered_text, True)
	pd.DataFrame(monogram_occurences_ws.items(),columns=["Monogram","Count"], index=None).to_excel(writer, sheet_name="CO_MG_WS", index=False)

	# count bigrams without overlapping
	(not_overlapped_bigrams_occurences, not_overlapped_bigrams_total) = bigram_occurences(filtered_text, False, False)
	bigram_stat_dict_to_dataframe(not_overlapped_bigrams_occurences).to_excel(writer,sheet_name="CO_BG_NOT_OV")
	(not_overlapped_bigrams_occurences_ws, not_overlapped_bigrams_total_ws) = bigram_occurences(filtered_text, True, False)
	bigram_stat_dict_to_dataframe(not_overlapped_bigrams_occurences_ws).to_excel(writer,sheet_name="CO_BG_NOT_OV_WS")

	# count bigrams with overlapping
	(overlapping_bigrams_occurences, overlapping_bigrams_total) = bigram_occurences(filtered_text, False, True)
	bigram_stat_dict_to_dataframe(overlapping_bigrams_occurences).to_excel(writer,sheet_name="CO_BG_OV")
	(overlapping_bigrams_occurences_ws, overlapping_bigrams_total_ws) = bigram_occurences(filtered_text, True, True)
	bigram_stat_dict_to_dataframe(overlapping_bigrams_occurences_ws).to_excel(writer,sheet_name="CO_BG_OV_WS")

	# calculate monogram frequencies
	monogram_frequencies = calculate_ngram_frequencies(monogram_occurences_without_ws, monogram_total)
	pd.DataFrame(monogram_frequencies.items(),columns=["Frequency","Count"]).to_excel(writer, sheet_name="MG_FR", index=False)
	monogram_frequencies_ws = calculate_ngram_frequencies(monogram_occurences_ws, monogram_total_ws)
	pd.DataFrame(monogram_frequencies_ws.items(),columns=["Frequency","Count"]).to_excel(writer, sheet_name="MG_FR_WS", index=False)

	# calculate bigrams without overlapping frequencies
	not_overlapped_bigrams_frequencies = calculate_ngram_frequencies(not_overlapped_bigrams_occurences, not_overlapped_bigrams_total)
	bigram_stat_dict_to_dataframe(not_overlapped_bigrams_frequencies).to_excel(writer,sheet_name="BG_FR_NOT_OV")
	not_overlapped_bigrams_frequencies_ws = calculate_ngram_frequencies(not_overlapped_bigrams_occurences_ws, not_overlapped_bigrams_total_ws)
	bigram_stat_dict_to_dataframe(not_overlapped_bigrams_frequencies_ws).to_excel(writer,sheet_name="BG_FR_NOT_OV_WS")

	# calculate bigrams with overlapping frequencies
	overlapping_bigrams_frequencies = calculate_ngram_frequencies(overlapping_bigrams_occurences, overlapping_bigrams_total)
	bigram_stat_dict_to_dataframe(overlapping_bigrams_frequencies).to_excel(writer,sheet_name="BG_FR_OV")
	overlapping_bigrams_frequencies_ws = calculate_ngram_frequencies(overlapping_bigrams_occurences_ws, overlapping_bigrams_total_ws)
	bigram_stat_dict_to_dataframe(overlapping_bigrams_frequencies_ws).to_excel(writer,sheet_name="BG_FR_OV_WS")

	# close writer
	writer.close()
	print_green_blue_colored_pair(f"Monograms and bigrams stats were saved to",os.path.join(os.getcwd(),'lab_results.xlsx'))

	# calculate entropy via monogram frequencies
	entropy_via_monogram_frequencies = calc_entropy(monogram_frequencies)
	print_green_blue_colored_pair("H1:", entropy_via_monogram_frequencies)
	entropy_via_monogram_frequencies_ws = calc_entropy(monogram_frequencies_ws)
	print_green_blue_colored_pair("H1 with ws:", entropy_via_monogram_frequencies_ws)

	# calculate entropy via not overlapped frequencies
	entropy_via_not_overlapped_bigrams_frequencies = calc_entropy(not_overlapped_bigrams_frequencies)
	print_green_blue_colored_pair("H2 not overlapped:", entropy_via_not_overlapped_bigrams_frequencies)
	entropy_via_not_overlapped_bigrams_frequencies_ws = calc_entropy(not_overlapped_bigrams_frequencies_ws)
	print_green_blue_colored_pair("H2 not overlapped with ws:", entropy_via_not_overlapped_bigrams_frequencies_ws)

	# calculate entropy via overlapping frequencies
	entropy_via_overlapping_bigrams_frequencies = calc_entropy(overlapping_bigrams_frequencies)
	print_green_blue_colored_pair("H2 overlapping:", entropy_via_overlapping_bigrams_frequencies)
	entropy_via_overlapping_bigrams_frequencies_ws = calc_entropy(overlapping_bigrams_frequencies_ws)
	print_green_blue_colored_pair("H2 overlapping with ws:", entropy_via_overlapping_bigrams_frequencies_ws)
	

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
		
