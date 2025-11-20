import random

def trial_division(n):
    if n < 2: return False
    primes_filter = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
    for p in primes_filter:
        if n == p: return True
        if n % p == 0: return False
    return True

def miller_rabin_test(n, k=40):
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
            
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def get_random_prime(bits, debug_mode=False):
    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << bits - 1) | 1
        
        if trial_division(candidate):
            if miller_rabin_test(candidate):
                return candidate
            else:
                if debug_mode:
                    print(f" [x] Число {candidate} відсіяно тестом Міллера-Рабіна (складене).")

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = extended_gcd(b % a, a)
        return gcd, y - (b // a) * x, x

def modinv(a, m):
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        raise Exception('Помилка: Оберненого елемента не існує')
    return x % m

def GenerateKeyPair(bits=256, debug_mode=False):
    p = get_random_prime(bits, debug_mode)
    q = get_random_prime(bits, debug_mode)
    while p == q:
        q = get_random_prime(bits, debug_mode)
        
    n = p * q
    phi = (p - 1) * (q - 1)
    
    e = 65537
    while extended_gcd(e, phi)[0] != 1:
        e = random.randrange(3, phi, 2)
        
    d = modinv(e, phi)
    
    return ((d, p, q), (n, e))

def Encrypt(message_int, public_key):
    n, e = public_key
    if message_int >= n:
        raise ValueError("Повідомлення перевищує розмір модуля n!")
    return pow(message_int, e, n)

def Decrypt(ciphertext, private_key):
    d, p, q = private_key
    n = p * q
    return pow(ciphertext, d, n)

def Sign(message_int, private_key):
    d, p, q = private_key
    n = p * q
    return pow(message_int, d, n)

def Verify(message_int, signature, public_key):
    n, e = public_key
    check_val = pow(signature, e, n)
    return check_val == message_int

def SendKey(k, sender_priv, receiver_pub):
    k_encrypted = Encrypt(k, receiver_pub)
    k_signature = Sign(k, sender_priv)
    signature_encrypted = Encrypt(k_signature, receiver_pub)
    
    return k_encrypted, signature_encrypted

def ReceiveKey(package, receiver_priv, sender_pub):
    k_enc, s_enc = package
    
    k_decrypted = Decrypt(k_enc, receiver_priv)
    s_decrypted = Decrypt(s_enc, receiver_priv)
    
    if Verify(k_decrypted, s_decrypted, sender_pub):
        return k_decrypted
    else:
        return None

def text_to_int(text):
    return int.from_bytes(text.encode('utf-8'), 'big')

if __name__ == "__main__":
    print("\n>>> ЗАПУСК ЛАБОРАТОРНОЇ РОБОТИ №5: RSA <<<\n")

    print("1. Формування ключів (256 біт)")
    print("-----------------------------------")
    print(" -> Генеруємо пару для Абонента A...")
    
    priv_A, pub_A = GenerateKeyPair(256, debug_mode=True)
    
    print(f" [+] Знайдено прості числа для A:")
    print(f"    p = {priv_A[1]}")
    print(f"    q = {priv_A[2]}")

    print("\n -> Генеруємо пару для Абонента B...")
    while True:
        priv_B, pub_B = GenerateKeyPair(256, debug_mode=True)
        
        print(f"    Поточні p, q для B:\n    p = {priv_B[1]}\n    q = {priv_B[2]}")

        if pub_B[0] >= pub_A[0]:
            print(" [OK] Умова модулів виконана (n_B >= n_A).")
            break
        else:
            print("\n [!] Увага: Модуль B менший за A. Повторна генерація для коректності протоколу...\n")

    print("\n2. Згенеровані параметри криптосистеми")
    print("-----------------------------------")
    print("Користувач A:")
    print(f"  modulus (n) = {pub_A[0]}")
    print(f"  public exp (e) = {pub_A[1]}")
    print(f"  private exp (d) = {priv_A[0]}")
    print(f"  primes (p, q) = {priv_A[1]}, {priv_A[2]}")
    
    print("\nКористувач B:")
    print(f"  modulus (n) = {pub_B[0]}")
    print(f"  public exp (e) = {pub_B[1]}")
    print(f"  private exp (d) = {priv_B[0]}")
    print(f"  primes (p, q) = {priv_B[1]}, {priv_B[2]}")

    print("\n3. Демонстрація конфіденційності (Encrypt/Decrypt)")
    print("-----------------------------------")
    
    test_msg_num = random.randint(10**30, 10**31)
    print(f" Оригінальне повідомлення (число): {test_msg_num}")
    
    encrypted_c = Encrypt(test_msg_num, pub_B)
    print(f" Зашифровані дані (для B): {encrypted_c}")
    
    decrypted_m = Decrypt(encrypted_c, priv_B)
    print(f" Розшифровані дані (у B):  {decrypted_m}")
    
    if test_msg_num == decrypted_m:
        print(" >> Результат: Успіх! Дані збігаються.")
    else:
        print(" >> Результат: Помилка!")

    print("\n4. Демонстрація автентичності (Digital Signature)")
    print("-----------------------------------")
    
    sign_text = "LabWork_Done"
    print(f" Текст для підпису: '{sign_text}'")
    sign_int = text_to_int(sign_text)
    
    signature_val = Sign(sign_int, priv_A)
    print(f" Цифровий підпис користувача A: {signature_val}")
    
    verification_status = Verify(sign_int, signature_val, pub_A)
    print(f" Перевірка підпису публічним ключем A: {verification_status}")

    print("\n5. Протокол безпечного обміну ключами")
    print("-----------------------------------")
    
    secret_k = random.randint(10**45, 10**46)
    print(f" A генерує сесійний ключ k = {secret_k}")
    
    print(" A формує захищений пакет (SendKey)...")
    package_data = SendKey(secret_k, priv_A, pub_B)
    print(f" Відправлено кортеж (Encrypted_K, Encrypted_Sign)")
    
    print(" B отримує та розбирає пакет (ReceiveKey)...")
    received_val = ReceiveKey(package_data, priv_B, pub_A)
    
    print(f" B відновив значення k' = {received_val}")
    
    if received_val == secret_k:
        print(" >> Фінальний результат: Протокол виконано успішно. Автентифікація пройшла.")
    else:
        print(" >> Фінальний результат: Помилка протоколу.")
    
    print("\n>>> Роботу завершено <<<")