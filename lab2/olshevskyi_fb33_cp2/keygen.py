import random

RUSSIAN_ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

# Генерація випадкових ключів
def generate_random_key(length):
    """Генерує випадковий ключ заданої довжини"""
    return ''.join(random.choice(RUSSIAN_ALPHABET) for _ in range(length))

# Створюємо словник з випадковими ключами
key_examples = {}
for key_length in range(2, 21):
    key_examples[key_length] = generate_random_key(key_length)

# Виводимо результат
print("key_examples = {")
for length, key in key_examples.items():
    print(f"    {length}: '{key}',")
print("}")