import re

def clean_text(text):
    text = text.strip().lower()
    text = re.sub(r'[^а-яё]', '', text)  
    with open("texts/clean.txt", "w", encoding="utf-8") as f:
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

with open("texts/our_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

clean_msg = clean_text(text)

for idx, key in enumerate(pre_keys, 1):
    full_key = generate_full_key(clean_msg, key)
    encrypted = encrypt_vigenere(clean_msg, full_key)
    
    with open(f"texts/encrypted_{idx}_key_{key}.txt", "w", encoding="utf-8") as f:
        f.write(encrypted)
    
    print(f"Ключ {idx} ({key}): зашифровано, довжина={len(encrypted)}")

print(f"\nВсього створено {len(pre_keys)} шифротекстів")