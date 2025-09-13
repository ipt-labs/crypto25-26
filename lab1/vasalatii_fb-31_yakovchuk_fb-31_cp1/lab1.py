import argparse
from colorama import Fore, Style
from chardet.universaldetector import UniversalDetector
import magic
import math
import os

alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"

def print_error(error: str):
    print(Fore.RED + error + Style.RESET_ALL)

def calc_entropy(frequencies:list[float]) -> float:
	entropy = 0
	for frequency in frequencies:
		if frequency > 0:
			entropy -= frequency * math.log2(frequency)
	return entropy	

def process_text(content:str):
	print(f"{Fore.LIGHTGREEN_EX}Text length:{Fore.LIGHTBLUE_EX} {len(content)}{Style.RESET_ALL}")
	buffer = content.lower()
	prev_ch = None
	monograms_amount = 0
	monograms_count = {c: 0 for c in alphabet}
	not_overlapped_bigrams_count = {c1+c2:0 for c1 in alphabet for c2 in alphabet}
	overlapping_bigrams_count = not_overlapped_bigrams_count.copy()
	for ch in buffer:
		temp_ch = ch
		if ch not in alphabet:
			if ch == "ё":
				temp_ch = "е"
			elif ch == "ъ":
				temp_ch = "ь"
			else:
				continue
		monograms_count[temp_ch] += 1
		monograms_amount += 1
		if monograms_amount % 2 == 0:
			not_overlapped_bigrams_count[prev_ch+temp_ch] += 1
		if prev_ch is not None:
			overlapping_bigrams_count[prev_ch+temp_ch] += 1
		prev_ch = temp_ch
	print(monograms_amount)
	print(monograms_count)
	print(not_overlapped_bigrams_count)
	print(overlapping_bigrams_count)
	

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
				#TODO it would be better to warn about low confidence
				print(f"{Fore.LIGHTGREEN_EX}Encoding detection result:{Fore.LIGHTBLUE_EX} {detection_result}{Style.RESET_ALL}")
				with open(file_path, encoding=detector.result['encoding']) as f:
					content = f.read()
					process_text(content)
			else:
				print_error("Failed to detect encoding")	
		
