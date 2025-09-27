import argparse
from random import choice
from colorama import Fore, Style
from chardet.universaldetector import UniversalDetector
import magic
import os
import pandas as pd
from vigenere import VigenereCipher
from beautiful_prints import print_df, print_error, print_green_blue_colored_pair
from plots import barplot

def calculate_ic(text:str, r: int):
	total = 0
	symbol_count = {}
	for ch in text[::r]:
		total+=1
		if ch in symbol_count:
			symbol_count[ch] +=1
		else:
			symbol_count[ch] = 1
	return sum([count*(count-1) for count in list(symbol_count.values())])/(total*(total-1))

def gen_rand_word(alphabet:str, size:int):
	return "".join(choice(alphabet) for _ in range(size))

def process_text(content:str, basepath: str):
	alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
	filtered_text = ''.join(filter(lambda char: char in alphabet, content.strip().lower().replace("ё","е")))

	keys = [gen_rand_word(alphabet, i) for i in range(2, 31)]
	print_green_blue_colored_pair("Used random keys:", keys)

	print_green_blue_colored_pair("Index of coincidence of plain text:", calculate_ic(filtered_text, 1))

	stats = []
	for key in keys:
		ct = VigenereCipher(key, alphabet).encrypt(filtered_text)
		stats.append({
			 'key_len': len(key),'ic': calculate_ic(ct,1)
		})

	df = pd.DataFrame(stats)
	print_df(df)
	
	plot_dir = "plots"
	os.makedirs(plot_dir,exist_ok=True)
	barplot(df['key_len'], df['ic'], "Indexes of coincidence by different key lengths",
	        "Key length", "IC", True, 90, f"{os.path.join(plot_dir,basepath)}_ics_stats_barplot.png")


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
						process_text(content,f'{os.path.basename(file_path).split('.')[0]}')
				else:
					print_error("Failed to detect encoding")