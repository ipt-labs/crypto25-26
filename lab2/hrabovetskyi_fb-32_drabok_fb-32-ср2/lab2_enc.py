import matplotlib.pyplot as plt

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
M = len(ALPHABET)

def normalize_text(text):
    return "".join(ch for ch in text.lower() if ch in ALPHABET)

def repeat_key(key, length):
    key = key.lower()
    return (key * (length // len(key) + 1))[:length]

def vigenere_encrypt(text, key):
    text = normalize_text(text)
    key = normalize_text(key)
    key_full = repeat_key(key, len(text))
    encrypted = ""
    for t, k in zip(text, key_full):
        x = ALPHABET.index(t)
        y = ALPHABET.index(k)
        c = (x + y) % M
        encrypted += ALPHABET[c]
    return encrypted

def index_of_coincidence(text):
    text = normalize_text(text)
    N = len(text)
    freqs = [text.count(ch) for ch in ALPHABET]
    ic = sum(f * (f - 1) for f in freqs) / (N * (N - 1)) if N > 1 else 0
    return ic

input_file = "input.txt"
save_files = False  # змінити на True, якщо потрібно зберігати файли

keys = {
    2: "лу",
    3: "кот",
    4: "вода",
    5: "мирон",
    10: "шифрування",
    11: "жсчюгюдщйжвн",
    12: "фвсжтййярхтцв",
    13: "ьнтюжвчїфдшг",
    14: "чїчдшгювпфжцн",
    15: "взцбщтюпшгжцвн",
    16: "щфюеупвьйжцїждш",
    17: "цчфїєгдцчюїзщнжт",
    18: "зюцлгщчпвжшцждїжтр",
    19: "гїжювщцшщжвчпцждщєч",
    20: "шцчгдпюжшщфцждївпцшгр",
}

with open(input_file, "r", encoding="utf-8") as f:
    text = f.read()

plain_ic = index_of_coincidence(text)
print(f"Відкритий текст: IC = {plain_ic:.4f}")

ics = {"Відкритий текст": plain_ic}
for length, key in keys.items():
    encrypted_text = vigenere_encrypt(text, key)
    ic = index_of_coincidence(encrypted_text)
    ics[f"{length}"] = ic

    if save_files:
        output_file = f"encrypted_r{length}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(encrypted_text)
        print(f"Довжина ключа = {length}, ключ = {key} -> збережено у {output_file}")
    else:
        print(f"Довжина ключа = {length}, ключ = {key}, IC = {ic:.4f}")

plt.figure(figsize=(10, 6))
bars = plt.bar(list(ics.keys()), list(ics.values()), edgecolor='black')

plt.title("Залежність індексу відповідності від довжини ключа")
plt.xlabel("Довжина ключа")
plt.ylabel("Індекс відповідності (IC)")
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()