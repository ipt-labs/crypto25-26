alh = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def encrypt(text, key):
    cipher = ''
    k = 0
    for letter in text:
        cipher += alh[(alh.index(letter) + alh.index(key[k])) % 32]
        k += 1
        if k == len(key):
            k = 0
    return cipher

def decrypt(text, key):
    plain = ''
    k = 0
    for letter in text:
        plain += alh[(alh.index(letter) - alh.index(key[k])) % 32]
        k += 1
        if k == len(key):
            k = 0
    return plain
