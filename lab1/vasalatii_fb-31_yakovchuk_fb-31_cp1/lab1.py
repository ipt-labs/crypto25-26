from collections import Counter
import math

def calc_monogram_entropy(frequency_dict: Counter, n: int) -> float:
	entropy = 0
	for char, el in frequency_dict.items():
		frequency = el/n
		print(f"Symbol {char} frequency: {frequency}")
		entropy -=frequency * math.log2(frequency)
	return entropy

def calc_bigram_entropy(frequency_dict: Counter, n: int) -> float:
	entropy = 0
	for char, el in frequency_dict.items():
		frequency = el / n
		print(f"Symbol {char} frequency: {frequency}")
		entropy -= frequency * math.log2(frequency)
	return entropy

def parse_file(filename) -> str:
	with open(filename, encoding="ibm866") as f:
		txt = f.read()
		return txt

def main():
	file_path = "../../tasks/cp1/TEXT"
	buffer = parse_file(file_path)
	buffer.replace('\n', '')
	print(buffer)
	n = len(buffer)
	frequency_dict1 = Counter(buffer)
	mono_entropy = calc_monogram_entropy(frequency_dict1, n)
	frequency_dict2 = Counter(buffer[index:index+2] for index in range(0, n-1))

	print(f"Entropy of the given text: {round(entropy, 4)}")

if __name__ == "__main__":
	main()