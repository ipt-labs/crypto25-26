import argparse
from collections import Counter
from colorama import Fore, Style
from chardet.universaldetector import UniversalDetector
import magic
import math
import os

def print_error(error: str):
    print(Fore.RED + error + Style.RESET_ALL)

def calc_entropy(frequencies:list[float]) -> float:
	entropy = 0
	for frequency in frequencies:
		entropy -= frequency * math.log2(frequency)
	return entropy

def process_text(content:str):
	#TODO filter text (e.g. remove numbers, special chars, make all lowercase)
    buffer = content
    buffer.replace('\n', '')
    n = len(buffer)
    print(f"{Fore.LIGHTGREEN_EX}Text length:{Fore.LIGHTBLUE_EX} {n}{Style.RESET_ALL}")
    monogram_counts = Counter(buffer)
    bigrams_with_overlapping_counts = Counter(buffer[index:index+2] for index in range(0, n-1))
	#TODO do not forget about bigrams with overlapping


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
		
