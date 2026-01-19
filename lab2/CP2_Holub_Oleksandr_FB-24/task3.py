from random import choice
import csv


ALPHABET: str = 'абвгдежзийклмнопрстуфхцчшщыъьэюя'

def file_read(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        text: str = file.read()
    return text

def key_generate(key_len: int) -> str:
    key = ''.join(choice(ALPHABET) for i in range(key_len))
    return key

def create_blocks(encrypted_text: str, key_len: int) -> list:
    blocks: list = []
    for i in range(key_len):
        block = encrypted_text[i::key_len]
        blocks.append(block)
    return blocks

def affinity_index(encrypted_text: str) -> float:
    frequency: dict = {}
    affinity: float = 0.0
    for char in encrypted_text:
        if char in frequency:
            frequency[char] += 1
        else:
            frequency[char] = 1
    for char in frequency:
        affinity += (frequency[char] * (frequency[char] - 1)) / (len(encrypted_text) * (len(encrypted_text) - 1))
    return affinity

def create_csv_file(filename: str, affinity_dict: dict):
    with open(filename, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Довжина ключа", "Індекс"])
        for affinity in affinity_dict:
            key_len = len(affinity)
            affinity = affinity_dict[affinity]
            affinity = str(affinity).replace('.', ',')
            writer.writerow([key_len, affinity])


def main():
    text: str = file_read('C:\\Users\\Олександр\\Desktop\\CP2_Holub_Oleksandr_FB-24\\ext.txt')
    affinity_dict: dict = {}
    for i in range(2, 51):
        key = key_generate(i)
        text_blocks = create_blocks(text, len(key))
        affinity: int = 0
        for block in text_blocks:
            affinity += affinity_index(str(block))
        affinity_dict[key] = affinity / len(key)
    create_csv_file('Affinities_task3.csv', affinity_dict)


if __name__ == "__main__":
    main()
