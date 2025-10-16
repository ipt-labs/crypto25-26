def create_dict():
    russian = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    letter_to_index = {}
    index_to_letter = {}
    for i, char in enumerate(russian):
        letter_to_index[char] = i
        index_to_letter[i] = char
    return letter_to_index, index_to_letter

def text_to_numb(text, letter_to_index):
    numbers = []
    for char in text:
        if char in letter_to_index:
            numbers.append(letter_to_index[char])
    return numbers

def encrypt_vigenere(text_num, key_num):
    encrypt_num =[]
    key_length = len(key_num)
    alphabet_length = 32
    for i, num in enumerate(text_num):
        key_value = key_num[i % key_length]
        encrypted_value = (num + key_value) % alphabet_length
        encrypt_num.append(encrypted_value)
    return encrypt_num

def decrypt_vigenere(encrypted_num, key_num):
    decrypted_num = []
    key_length = len(key_num)
    alphabet_length = 32
    for i, num in enumerate(encrypted_num):
        key_value = key_num[i % key_length]
        decrypted_value = (num - key_value + alphabet_length) % alphabet_length
        decrypted_num.append(decrypted_value)
    return decrypted_num

def index_vidpovid(numbers):
    N=len(numbers)
    freq = [0]*32
    for num in numbers:
        freq[num] += 1
    
    sum = 0
    for f in freq:
        sum += f*(f-1)
    ic = sum / (N*(N-1))

    return ic

with open("task1_cleaned.txt", "r", encoding="utf-8") as file:
    text = file.read()
key = {
    2: 'ум',
    3: 'век',
    4: 'глаз',
    5: 'земля',
    12: 'криптография'
}
letter_to_index, index_to_letter = create_dict()
key_num = {}
for k, v in key.items():
    key_num[k] = text_to_numb(v, letter_to_index)

text_numbers = text_to_numb(text, letter_to_index)

chosen_key_num = key_num[12]

encrypted_numbers = encrypt_vigenere(text_numbers, chosen_key_num)
# decrypted_numbers = decrypt_vigenere(encrypted_numbers, chosen_key_num)

encrypted_text = ''.join(index_to_letter[num] for num in encrypted_numbers)
# decrypted_text = ''.join(index_to_letter[num] for num in decrypted_numbers)
# print(encrypted_text)
# print(decrypted_text == text)
ic_plain = index_vidpovid(text_numbers)
print(f"IC plain text: {ic_plain}")
ic_encrypted = index_vidpovid(encrypted_numbers)
print(f"IC encrypted text: {ic_encrypted}")