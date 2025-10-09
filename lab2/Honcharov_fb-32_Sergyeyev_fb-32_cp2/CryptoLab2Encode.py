import re
import matplotlib.pyplot as plt

CYRYalphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

keys = ["сб","сяв","ччжд","стэйй","тяюгшазэей","мдйчфььвмбж","нгщеякзкйюця",
"зныкгмшпьцугп","жшвцойуычнюнаь","оякврткжйпнааэа",
"жбьуьжмчыотсчюдт","збчикчккиьщуюсфнш","шзчушуеябщцмюмшиот",
"згитххезцпрцгжпишбф","эичиырхяикчшфкужосхд"]

def index_of_coincidence(text: str) -> float:
    letters = [ch for ch in text if ch in CYRYalphabet]
    N = len(letters)
    if N <= 1:
        return 0.0
    freq = {ch: letters.count(ch) for ch in CYRYalphabet}
    numerator = sum(f * (f - 1) for f in freq.values())
    denominator = N * (N - 1)
    return numerator / denominator

def process_text(text):
    text = text.lower()
    text = re.sub(r'[^а-яё\s]', ' ', text)
    text = text.replace('ё', 'е')
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace(" ", "")
    return text

def vigenere_encrypt(plaintext: str, key: str) -> str:
    alphabet = CYRYalphabet

    key_u = ''.join(ch for ch in key.lower() if ch in alphabet)
    key_len = len(key_u)

    ciphertext = []
    key_pos = 0

    for ch in plaintext:
        if ch in alphabet:
            shift = alphabet.index(key_u[key_pos % key_len])
            new_ch = alphabet[(alphabet.index(ch) + shift) % len(alphabet)]
            ciphertext.append(new_ch)
            key_pos += 1
        else:
            ciphertext.append(ch)
    return "".join(ciphertext)

def main():
    filename = "./text.txt"
    with open(filename, "r", encoding="utf-8") as f:
        raw_text = f.read()

    M = process_text(raw_text)
    with open("cleaned_text.txt", "w", encoding="utf-8") as f:
        f.write(M)

    textes = {}
    for key in keys:
        C = vigenere_encrypt(M, key)
        textes[key] = C
        print(f"{len(key)}: {key}")

    frequences = {}
    frequences[0] = index_of_coincidence(M)
    print(f"0: {frequences[0]}")
    for textkey in textes:
        frequences[len(textkey)] = index_of_coincidence(textes[textkey])
        print(f"{textkey}: {frequences[len(textkey)]}")

    plt.figure(figsize=(10,6))
    plt.bar(frequences.keys(), frequences.values(), color="skyblue", edgecolor="black")
    plt.xlabel("Ключ / Текст", fontsize=12)
    plt.ylabel("Index of Coincidence", fontsize=12)
    plt.title("Index of Coincidence", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
