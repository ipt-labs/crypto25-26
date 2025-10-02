files = ["first.txt", "second.txt"] 
russian = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
import re

with open("merged1.txt", "w", encoding="utf-8") as outfile:
    for fname in files:
        with open(fname, "r", encoding="cp1251") as infile:
            text = infile.read()
            text = text.lower()
            text = re.sub(f"[^ {russian}]", " ", text)
        outfile.write(text)
        outfile.write("\n")


with open("merged_without_spaces.txt", "w", encoding="utf-8") as outfile:
    for fname in files:
        with open(fname, "r", encoding="cp1251") as infile:
            text = infile.read()
            text = text.lower()
            text = re.sub(f"[^{russian}]", "", text)  
        outfile.write(text)