from vigenere import encrypt, alh

keys = [
    'ау',
    'дно',
    'куда',
    'можно',
    'достижение',
    'воображение',
    'многообразие',
    'автоматизация',
    'взаимодействие',
    'непосредственно',
    'экспериментально',
    'предусмотрительно',
    'производительность',
    'электрооборудование',
    'антирадиолокационный'
]

with open('sample.txt', 'r', encoding='utf8') as f:
    text = f.read().lower()
    text = ''.join(c for c in text if c in alh)

with open('sample_cleaned.txt', 'w', encoding='utf8') as f:
    f.write(text)

print(f'Text length: {len(text)}')
print()

for key in keys:
    cipher = encrypt(text, key)
    filename = f'cipher-{len(key)}.txt'
    with open(filename, 'w', encoding='utf8') as f:
        f.write(cipher)
    print(f'{key} (r={len(key)}) -> {filename}')
