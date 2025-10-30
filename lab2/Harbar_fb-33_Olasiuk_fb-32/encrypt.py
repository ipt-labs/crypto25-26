import re
from collections import Counter   

def clean_text(text):
    text = text.strip().lower()
    text = re.sub(r'[^а-яё]', '', text)  
    with open("clean.txt", "w", encoding="utf-8") as f:
        f.write(text)
    return text

pre_keys = [
    'аз', 'нчм', 'збмж', 'абезю', 'цнчмйнзхуе', 'нфтшюлахииг', 'мёюищыъчефьж',
    'нщйсдзяегухшы', 'емзщлкгюьбанцв', 'щакьпгмърйыэифё', 'зпюлёцчужийктшфщ',
    'цнжйоряскфмёщтигх', 'ипюцйьыэкзурнхфеёг', 'ьрйыюкидёнуэщсфзлеа', 'фолвйяьзшжмчыъгещкёд'
]

def generate_full_key(msg, key):
    full_key = []
    for i in range(len(msg)):
        full_key.append(key[i % len(key)])
    return "".join(full_key)

def encrypt_vigenere(msg, key):
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    encrypted_text = []
    
    for i in range(len(msg)):
        char = msg[i]
        if char in alphabet:
            char_index = alphabet.index(char)
            key_index = alphabet.index(key[i])
            encrypted_index = (char_index + key_index) % len(alphabet)
            encrypted_text.append(alphabet[encrypted_index])
        else:
            encrypted_text.append(char)
    
    return "".join(encrypted_text)

def calculate_ic(text):
    n = len(text)
    if n <= 1:
        return 0
    freq = Counter(text)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

with open("texts/our_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

clean_msg = clean_text(text)

ic_plain = calculate_ic(clean_msg)
print(f"Індекс відповідності для відкритого тексту: {ic_plain:.5f}\n")

for idx, key in enumerate(pre_keys, 1):
    full_key = generate_full_key(clean_msg, key)
    encrypted = encrypt_vigenere(clean_msg, full_key)
    
    with open(f"texts/encrypted_{idx}_key_{key}.txt", "w", encoding="utf-8") as f:
        f.write(encrypted)
    
    ic_cipher = calculate_ic(encrypted)
    print(f"Ключ {idx}: IC={ic_cipher:.5f}")

print(f"\nВсього створено {len(pre_keys)} шифротекстів")
