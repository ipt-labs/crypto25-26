import random

# ------------------------------------------------------------
# Допоміжні функції для відображення даних
# ------------------------------------------------------------
def display_data(label, value):
    if isinstance(value, int):
        print(f"{label}: {value}  | Шістнадцяткове: {hex(value)[2:].upper()}")
    else:
        print(f"{label}: {value}")
    print("—" * 35)


# ------------------------------------------------------------
# Розширений алгоритм Евкліда
# ------------------------------------------------------------
def extended_gcd(a_val, b_val):
    if a_val == 0:
        return b_val, 0, 1
    gcd_val, x1_val, y1_val = extended_gcd(b_val % a_val, a_val)
    return gcd_val, y1_val - (b_val // a_val) * x1_val, x1_val


# ------------------------------------------------------------
# Обчислення оберненого елемента за модулем
# ------------------------------------------------------------
def modular_inverse(a_val, modulus):
    gcd_val, x_val, _ = extended_gcd(a_val, modulus)
    if gcd_val != 1:
        raise ValueError("Обернений елемент не існує: числа не взаємно прості.")
    return x_val % modulus


# ------------------------------------------------------------
# Швидке піднесення до степеня за модулем
# ------------------------------------------------------------
def power_mod(base_val, exponent, modulus_val):
    result = 1
    base_val %= modulus_val
    while exponent > 0:
        if exponent & 1:
            result = (result * base_val) % modulus_val
        base_val = (base_val * base_val) % modulus_val
        exponent >>= 1
    return result


# ------------------------------------------------------------
# Перевірка числа на простоту (тест Міллера-Рабіна)
# ------------------------------------------------------------
def check_prime(n_val, test_rounds=40):
    if n_val in (2, 3):
        return True
    if n_val < 2 or n_val % 2 == 0:
        return False

    # Запис n-1 = d * 2^s
    s_count = 0
    d_val = n_val - 1
    while d_val % 2 == 0:
        s_count += 1
        d_val //= 2

    for _ in range(test_rounds):
        a_val = random.randrange(2, n_val - 1)
        x_val = power_mod(a_val, d_val, n_val)
        if x_val in (1, n_val - 1):
            continue
        for _ in range(s_count - 1):
            x_val = power_mod(x_val, 2, n_val)
            if x_val == n_val - 1:
                break
        else:
            return False
    return True


# ------------------------------------------------------------
# Генерація простого числа заданої довжини
# ------------------------------------------------------------
def generate_prime_number(bit_length):
    # Невеликий набір малих простих для попереднього відсіву кандидатів
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    while True:
        candidate = random.getrandbits(bit_length)
        # Забезпечуємо старший біт = 1 (довжина в бітах) і непарність
        candidate |= (1 << (bit_length - 1)) | 1

        if any(candidate % p == 0 for p in small_primes):
            continue

        if check_prime(candidate):
            return candidate


# ------------------------------------------------------------
# ДЕМО: генерація кандидатів у прості (для звіту)
# ------------------------------------------------------------
def demo_prime_generation(bit_length=32, samples=10):
    """
    Демонструє, як відсіюються кандидати у прості:
    - діляться на малий простий;
    - не проходять Міллера-Рабіна;
    - стають простими.

    bit_length – довжина кандидатів у бітах (для звіту зручно 16/32, а не 256).
    samples – скільки кандидатів показати.
    """
    print("\n" + "=" * 60)
    print("ДЕМО ГЕНЕРАЦІЇ ПРОСТИХ ЧИСЕЛ (КАНДИДАТИ ТА ВІДСІВ)")
    print("=" * 60)

    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    found_primes = 0

    for i in range(samples):
        candidate = random.getrandbits(bit_length)
        candidate |= (1 << (bit_length - 1)) | 1  # старший біт і непарність

        print(f"\n[{i + 1}] Кандидат:")
        display_data("candidate", candidate)

        # Перевірка на подільність малими простими
        divisible_by = None
        for p in small_primes:
            if candidate % p == 0:
                divisible_by = p
                break

        if divisible_by is not None:
            print(f"   -> ВІДСІЯНО МАЛИМИ ПРОСТИМИ (ділиться на {divisible_by})")
            continue

        # Якщо не ділиться на малі – проганяємо Міллера-Рабіна
        if check_prime(candidate):
            print("   -> ПРОСТЕ ЧИСЛО (пройшов тест Міллера-Рабіна)")
            found_primes += 1
        else:
            print("   -> СКЛАДЕНЕ (завалив тест Міллера-Рабіна)")

    print("\nПІДСУМОК: знайдено простих серед кандидатів:", found_primes)
    print("=" * 60 + "\n")


# ------------------------------------------------------------
# Перетворення текст ↔ число
# ------------------------------------------------------------
def text_to_number(text_str):
    return int.from_bytes(text_str.encode("utf-8"), "big")


def number_to_text(num_val):
    byte_length = (num_val.bit_length() + 7) // 8
    if byte_length == 0:
        return ""
    try:
        return num_val.to_bytes(byte_length, "big").decode("utf-8")
    except Exception:
        return "[неможливо конвертувати в текст]"


# ------------------------------------------------------------
# Генерація ключової пари RSA
# ------------------------------------------------------------
def GenerateKeyPair(bit_size=256):
    """
    Генерує пару ключів RSA.
    bit_size – довжина КОЖНОГО простого p і q в бітах (не модуля n).
    """
    prime_p = generate_prime_number(bit_size)
    prime_q = generate_prime_number(bit_size)
    while prime_q == prime_p:
        prime_q = generate_prime_number(bit_size)

    modulus_n = prime_p * prime_q
    euler_phi = (prime_p - 1) * (prime_q - 1)

    public_exp = 65537
    # Якщо 65537 не підходить, шукаємо інший непарний e
    while extended_gcd(public_exp, euler_phi)[0] != 1:
        public_exp = random.randrange(3, euler_phi - 1, 2)

    private_exp = modular_inverse(public_exp, euler_phi)
    return (public_exp, modulus_n), (private_exp, prime_p, prime_q)


# ------------------------------------------------------------
# Основні операції RSA
# ------------------------------------------------------------
def Encrypt(number, public_key):
    exp_e, modulus_n = public_key
    if number >= modulus_n:
        raise ValueError("Число перевищує розмір модуля.")
    return power_mod(number, exp_e, modulus_n)


def Decrypt(cipher_number, private_key):
    exp_d, prime_p, prime_q = private_key
    return power_mod(cipher_number, exp_d, prime_p * prime_q)


def Sign(number, private_key):
    exp_d, prime_p, prime_q = private_key
    return power_mod(number, exp_d, prime_p * prime_q)


def Verify(number, signature_value, public_key):
    exp_e, modulus_n = public_key
    return power_mod(signature_value, exp_e, modulus_n) == number


# ------------------------------------------------------------
# Відправлення секретного ключа
# ------------------------------------------------------------
def SendKey(session_key, private_key_sender, public_key_recipient):
    e_recipient, n_recipient = public_key_recipient
    d_sender, p_sender, q_sender = private_key_sender
    n_sender = p_sender * q_sender

    if n_recipient < n_sender:
        raise ValueError("Модуль отримувача замалий для передачі.")

    signed_key = Sign(session_key, private_key_sender)
    encrypted_key = Encrypt(session_key, public_key_recipient)
    encrypted_signature = Encrypt(signed_key, public_key_recipient)

    return encrypted_key, encrypted_signature


# ------------------------------------------------------------
# Отримання та аутентифікація ключа
# ------------------------------------------------------------
def ReceiveKey(encrypted_key, encrypted_signature, private_key_recipient, public_key_sender):
    decrypted_key = Decrypt(encrypted_key, private_key_recipient)
    decrypted_signature = Decrypt(encrypted_signature, private_key_recipient)

    is_valid = Verify(decrypted_key, decrypted_signature, public_key_sender)
    return decrypted_key, is_valid


# ------------------------------------------------------------
# Демонстраційний сценарій
# ------------------------------------------------------------
def demonstration():
    # --------------------------------------------------------
    # [0] ДЕМО генерації кандидатів у прості (для звіту)
    # --------------------------------------------------------
    # Для звіту можна збільшити bit_length, але для читабельності залишу 32 біти
    demo_prime_generation(bit_length=32, samples=10)

    # --------------------------------------------------------
    # [1] Генерація ключових пар для A та B
    # --------------------------------------------------------
    print("▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌")
    print("▐             ДЕМОНСТРАЦІЯ RSA          ▌")
    print("▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌\n")

    print("[1] Генерація ключових пар A і B...\n")

    public_A, private_A = GenerateKeyPair()
    public_B, private_B = GenerateKeyPair()

    # Гарантуємо умову n_B >= n_A (як у завданні pq <= p1*q1)
    while public_B[1] < public_A[1]:
        public_B, private_B = GenerateKeyPair()

    e_A, n_A = public_A
    d_A, p_A, q_A = private_A
    e_B, n_B = public_B
    d_B, p_B, q_B = private_B

    phi_A = (p_A - 1) * (q_A - 1)
    phi_B = (p_B - 1) * (q_B - 1)

    print("Ключі абонента A:")
    display_data("p(A)", p_A)
    display_data("q(A)", q_A)
    display_data("n(A) = p(A)*q(A)", n_A)
    display_data("φ(n(A))", phi_A)
    display_data("e(A)", e_A)
    display_data("d(A)", d_A)
    print(
        f"Бітова довжина p(A): {p_A.bit_length()} | q(A): {q_A.bit_length()} | n(A): {n_A.bit_length()}"
    )
    print("—" * 35)

    print("Ключі абонента B:")
    display_data("p(B)", p_B)
    display_data("q(B)", q_B)
    display_data("n(B) = p(B)*q(B)", n_B)
    display_data("φ(n(B))", phi_B)
    display_data("e(B)", e_B)
    display_data("d(B)", d_B)
    print(
        f"Бітова довжина p(B): {p_B.bit_length()} | q(B): {q_B.bit_length()} | n(B): {n_B.bit_length()}"
    )
    print("—" * 35)

    # --------------------------------------------------------
    # [2] Вибір випадкового відкритого повідомлення M
    # --------------------------------------------------------
    print("\n[2] Вибір випадкового відкритого повідомлення M\n")

    # Щоб M < n(A) і M < n(B), достатньо M < n(A), бо n_B >= n_A
    M = random.randrange(1, n_A)
    display_data("Випадкове повідомлення M", M)

    # --------------------------------------------------------
    # [3] Шифрування / розшифрування для A та для B
    # --------------------------------------------------------
    print("\n[3] Шифрування та розшифрування для A і B\n")

    # A шифрує і розшифровує "свій" M
    C_A = Encrypt(M, public_A)
    display_data("C_A = M^e(A) mod n(A)", C_A)
    M_dec_A = Decrypt(C_A, private_A)
    display_data("M_dec_A = C_A^d(A) mod n(A)", M_dec_A)
    print("Перевірка для A:", "OK" if M_dec_A == M else "ПОМИЛКА")
    print("—" * 35)

    # B шифрує і розшифровує той самий M
    C_B = Encrypt(M, public_B)
    display_data("C_B = M^e(B) mod n(B)", C_B)
    M_dec_B = Decrypt(C_B, private_B)
    display_data("M_dec_B = C_B^d(B) mod n(B)", M_dec_B)
    print("Перевірка для B:", "OK" if M_dec_B == M else "ПОМИЛКА")
    print("—" * 35)

    # --------------------------------------------------------
    # [4] Цифрові підписи абонентів A та B
    # --------------------------------------------------------
    print("\n[4] Цифрові підписи абонентів A та B\n")

    # Підпис A
    S_A = Sign(M, private_A)  # S_A = M^d(A) mod n(A)
    display_data("Підпис S_A = M^d(A) mod n(A)", S_A)
    valid_A = Verify(M, S_A, public_A)  # перевірка M ?= S_A^e(A) mod n(A)
    print("Перевірка підпису A:", "ПІДТВЕРДЖЕНО" if valid_A else "НЕДІЙСНИЙ")
    print("—" * 35)

    # Підпис B
    S_B = Sign(M, private_B)  # S_B = M^d(B) mod n(B)
    display_data("Підпис S_B = M^d(B) mod n(B)", S_B)
    valid_B = Verify(M, S_B, public_B)  # перевірка M ?= S_B^e(B) mod n(B)
    print("Перевірка підпису B:", "ПІДТВЕРДЖЕНО" if valid_B else "НЕДІЙСНИЙ")
    print("—" * 35)

    # --------------------------------------------------------
    # [5] Додатково: шифрування текстового повідомлення (для наочності)
    # --------------------------------------------------------
    print("\n[5] Шифрування текстового повідомлення для B\n")

    original_text = "Лабораторна-Томашевський-Ткач"
    print("Вихідний текст:", original_text)

    numeric_message = text_to_number(original_text)
    display_data("Числове представлення тексту", numeric_message)

    if numeric_message >= n_B:
        print("УВАГА: числове представлення тексту перевищує модуль n(B),")
        print("       для реальної системи потрібен паддінг/розбиття на блоки.")
    else:
        encrypted_message = Encrypt(numeric_message, public_B)
        display_data("Шифротекст C_text", encrypted_message)

        decrypted_number = Decrypt(encrypted_message, private_B)
        display_data("Розшифроване значення M_text", decrypted_number)
        print("Декодований текст:", number_to_text(decrypted_number))

    # --------------------------------------------------------
    # [6] Протокол обміну сеансовим ключем A → B
    # --------------------------------------------------------
    print("\n[6] Протокол обміну сеансовим ключем (A → B)\n")

    # Сеансовий ключ 0 < k < n(A) (і автоматично < n(B))
    session_key = random.randrange(1, n_A)
    display_data("Згенерований сеансовий ключ k", session_key)

    try:
        # Відправка через високорівневі процедури
        encrypted_key, encrypted_sig = SendKey(session_key, private_A, public_B)
        print("Відправлено зашифрований ключ k1 та підпис S1.\n")

        # Логування S, k1, S1 для звіту
        signed_key = Sign(session_key, private_A)  # S = k^d(A) mod n(A)
        display_data("Підпис S = k^d(A) mod n(A)", signed_key)
        display_data("k1 = k^e(B) mod n(B)", encrypted_key)
        display_data("S1 = S^e(B) mod n(B)", encrypted_sig)

        # Прийом ключа B
        received_key, authenticity = ReceiveKey(
            encrypted_key, encrypted_sig, private_B, public_A
        )
        display_data("k' = k1^d(B) mod n(B)", received_key)

        # Відновимо S' явно для журналу (результат розшифрування S1)
        decrypted_signature_on_B = Decrypt(encrypted_sig, private_B)
        display_data("S' = S1^d(B) mod n(B)", decrypted_signature_on_B)

        auth_status = "АУТЕНТИФІКАЦІЯ ПРОЙДЕНА" if authenticity else "ПОМИЛКА АУТЕНТИФІКАЦІЇ"
        print("Статус перевірки підпису A на ключі k':", auth_status)

        if received_key == session_key and authenticity:
            print("\n" + "=" * 55)
            print("   ПРОТОКОЛ УСПІШНО ВИКОНАНО: k' = k, підпис валідний")
            print("=" * 55)
        else:
            print("\nПРОТОКОЛ НЕВДАЛИЙ: або ключі різні, або підпис невалідний.")
    except Exception as e:
        print(f"Помилка при обміні ключами: {e}")


if __name__ == "__main__":
    demonstration()
