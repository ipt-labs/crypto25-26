from typing import List, Tuple

ALPHABET_STR = "абвгдежзийклмнопрстуфхцчшщьыэюя"
M = len(ALPHABET_STR)
M_SQUARED = M * M

RUSSIAN_FREQS = {'о': 0.1097, 'е': 0.0845}

CHAR_TO_INT = {char: i for i, char in enumerate(ALPHABET_STR)}
INT_TO_CHAR = {i: char for i, char in enumerate(ALPHABET_STR)}

KEYS_FILE = "key_candidates.txt"
CIPHERTEXT_FILE = "13.txt"

def egcd(a: int, n: int) -> Tuple[int, int]:
    r_prev, r_curr = a, n
    u_prev, u_curr = 1, 0
    while r_curr != 0:
        q = r_prev // r_curr
        r_prev, r_curr = r_curr, r_prev - q * r_curr
        u_prev, u_curr = u_curr, u_prev - q * u_curr
    return r_prev, u_prev

def mod_inverse(a: int, n: int) -> int | None:
    gcd, u = egcd(a, n)
    if gcd != 1:
        return None
    else:
        return u % n

def bigram_to_int(bigram: str) -> int:
    try:
        x1 = CHAR_TO_INT[bigram[0]]
        x2 = CHAR_TO_INT[bigram[1]]
        return x1 * M + x2
    except KeyError:
        return -1

def int_to_bigram(val: int) -> str:
    x1 = val // M
    x2 = val % M
    return INT_TO_CHAR[x1] + INT_TO_CHAR[x2]

def decrypt(ciphertext: str, a: int, b: int) -> str | None:
    a_inv = mod_inverse(a, M_SQUARED)
    if a_inv is None:
        print(f"Помилка: для 'a'={a} не існує оберненого елемента mod {M_SQUARED}")
        return None

    plaintext = []
    for i in range(0, len(ciphertext) - 1, 2):
        bigram = ciphertext[i:i + 2]
        Y = bigram_to_int(bigram)
        if Y == -1:
            continue

        X = (a_inv * (Y - b)) % M_SQUARED
        plaintext.append(int_to_bigram(X))

    return "".join(plaintext)

def calculate_fitness(text: str) -> float:
    if not text:
        return float('inf')

    text_len = len(text)

    freq_o = text.count('о') / text_len
    freq_e = text.count('е') / text_len

    error = 0.0
    error += (freq_o - RUSSIAN_FREQS['о']) ** 2
    error += (freq_e - RUSSIAN_FREQS['е']) ** 2

    return error

def load_keys(filename: str) -> List[Tuple[int, int]]:
    keys = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    keys.append((int(parts[0]), int(parts[1])))
    except FileNotFoundError:
        print(f"Помилка: Файл ключів '{filename}' не знайдено")
        return []
    except Exception as e:
        print(f"Помилка при читанні файлу ключів: {e}")
        return []

    print(f"Завантажено {len(keys)} ключів-кандидатів з '{filename}'")
    return keys

def load_ciphertext(filename: str) -> str:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return "".join(f.read().split())
    except FileNotFoundError:
        print(f"Помилка: Файл шифртексту '{filename}' не знайдено")
        print(f"Будь ласка, створіть цей файл та помістіть у нього шифртекст")
        return ""
    except Exception as e:
        print(f"Помилка при читанні шифртексту: {e}")
        return ""


def main():
    keys = load_keys(KEYS_FILE)
    if not keys:
        return

    ciphertext = load_ciphertext(CIPHERTEXT_FILE)
    if not ciphertext:
        return

    print("Зараз буде щось цікаве")

    best_key = None
    best_text = ""
    best_score = float('inf')

    for a, b in keys:
        plaintext = decrypt(ciphertext, a, b)
        if plaintext:
            score = calculate_fitness(plaintext)

            if score < best_score:
                best_score = score
                best_key = (a, b)
                best_text = plaintext

    if best_key:
        print(f"\nЗнайдено найкращий ключ (a, b): {best_key}")
        print(f"Оцінка (чим менше, тим краще): {best_score:.6e}")
        print("\nПочаток дешифрованого тексту:")
        print(best_text[:50])
        output_file = "decrypted_text.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(best_text)
    else:
        print("Не вдалося знайти жодного робочого ключа")

if __name__ == "__main__":
    main()