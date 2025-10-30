import re
russian = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


with open("task1.txt", "r", encoding="utf-8") as infile:
        text = infile.read()
        text = text.lower()
        text = text.replace("ё", "е")
        text = re.sub(f"[^{russian}]", "", text) 

with open("task1_cleaned.txt", "w", encoding="utf-8") as outfile:        
    outfile.write(text)