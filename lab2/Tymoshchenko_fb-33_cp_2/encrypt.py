from collections import Counter

def vigenere(text, key):
    alphabet_upper = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    alphabet_lower = alphabet_upper.lower()
    encrypted = []
    key_index = 0

    for char in text:
        if char in alphabet_upper:
            shift = alphabet_upper.index(key[key_index % len(key)].upper())
            encrypted_char = alphabet_upper[(alphabet_upper.index(char) + shift) % len(alphabet_upper)]
            encrypted.append(encrypted_char)
            key_index += 1
        elif char in alphabet_lower:
            shift = alphabet_upper.index(key[key_index % len(key)].upper())
            encrypted_char = alphabet_lower[(alphabet_lower.index(char) + shift) % len(alphabet_lower)]
            encrypted.append(encrypted_char)
            key_index += 1
        else:
            encrypted.append(char)
    return ''.join(encrypted)


def icdef(text):
    alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    text = ''.join([ch.upper() for ch in text if ch.upper() in alphabet])
    n = len(text)
    if n < 2:
        return 0.0
    freq = Counter(text)
    numerator = sum(count * (count - 1) for count in freq.values())
    return numerator / (n * (n - 1))


def main():
    input = "input.txt"
    keys = ["од", "три", "чоти", "пьять", "рлфвтмеоиз","ущтмаржсшцв","гвдйжкьфснрв","йюцбуьктеинмп","гсшчзяхфжвдалп","пйщььевюсззъуск","жрчогымуьщлмкхкю","егмефэявйссодмфсо","чэбиемэрвдаесщзлгш","щдеквегмвкдтьрьоьст","рвгчнмщмэфжнцкыдцлжо"] 

    with open(input, "r", encoding="utf-8") as f:
        text = f.read()
    icopen = icdef(text)
    print(f"Відкритий текст - Індекс відповідності: {icopen:.5f}")
    for key in keys:
        encrypted_text = vigenere(text, key)
        ic = icdef(encrypted_text)
        print(f"Ключ: '{key}' - Індекс відповідності: {ic:.5f}")

        output_file = f"encrypted_{key}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(encrypted_text)

if __name__ == "__main__":
    main()
