import random
def horner_pow(base, exponent, modulus):
    y = 1
    binary_exponent = bin(exponent)[2:]
  
    for bit in binary_exponent:
        y = (y * y) % modulus
      
        if bit == '1':
            y = (y * base) % modulus
          
    return y
  
def extended_euclid(a, b):
    x0, x1 = 1, 0
    y0, y1 = 0, 1
  
    while b != 0:
        q = a // b
        a, b = b, a % b
      
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
      
    return a, x0, y0
  
def modular_inverse(a, mod):
    gcd, x, _ = extended_euclid(a, mod)
    return x % mod
  
def find_gcd(a, b):
    while b:
        a, b = b, a % b
      
    return a
  
def check_small_divisors(n):
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
  
    for p in primes:
        if n % p == 0:
            return False
          
    return True
  
def probabilistic_primality_test(p, k=40):
    if p % 2 == 0:
        return False
      
    s = 0
    d_prime = p - 1
  
    while d_prime % 2 == 0:
        d_prime //= 2
        s += 1
      
    for _ in range(k):
        x = random.randint(2, p - 1)
        if find_gcd(x, p) > 1:
            return False
          
        x_r = horner_pow(x, d_prime, p)
      
        if x_r == 1 or x_r == p - 1:
            continue
          
        is_strong = False
        for _ in range(1, s):
            x_r = horner_pow(x_r, 2, p)
            if x_r == p - 1:
                is_strong = True
                break
              
            if x_r == 1:
                return False
              
        if not is_strong:
            return False
          
    return True
  
def generate_prime_with_rejects(bits, max_rejects=10):
    rejected = []
    while True:
        candidate = random.getrandbits(bits)
        if candidate % 2 == 0:
            candidate += 1
          
        reason = None
      
        if not check_small_divisors(candidate):
            reason = "відкинуто пробними діленнями"
          
        elif not probabilistic_primality_test(candidate):
            reason = "відкинуто тестом Міллера-Рабіна"
          
        if reason:
            if len(rejected) < max_rejects:
                rejected.append((candidate, reason))
              
            continue
        return candidate, rejected
      
def GenerateKeyPair(p, q, e=65537, label=""):
    n = p * q
    phi_n = (p - 1) * (q - 1)
  
    d = modular_inverse(e, phi_n)
  
    public_key = (e, n)
    private_key = (d, n)
  
    print(f"--- ЗГЕНЕРОВАНІ КЛЮЧІ {label} ---")
    print(f"Секретний ключ (d, p, q):\n d = {hex(d)[2:].upper()}\n p = {hex(p)[2:].upper()} ({p.bit_length()} біт)\n q = {hex(q)[2:].upper()} ({q.bit_length()} біт)")
    print(f"\nВідкритий ключ (n, e):\n n = {hex(n)[2:].upper()} ({n.bit_length()} біт)\n e = {e}")
    print("-----------------------------------")
  
    return public_key, private_key
  
def Encrypt(message, public_key):
    e, n = public_key
    return horner_pow(message, e, n)
  
def Decrypt(ciphertext, private_key):
    d, n = private_key
    return horner_pow(ciphertext, d, n)
  
def Sign(message, private_key):
    d, n = private_key
    return horner_pow(message, d, n)
  
def Verify(message, signature, public_key):
    e, n = public_key
    return horner_pow(signature, e, n) == message
  
def SendKey(k, sender_priv, recipient_pub):
    d, n = sender_priv
    e1, n1 = recipient_pub
  
    s = Sign(k, sender_priv)
  
    k1 = horner_pow(k, e1, n1)
    s1 = horner_pow(s, e1, n1)
    return k1, s1
  
def ReceiveKey(payload, recipient_priv, sender_pub):
    k1, s1 = payload
    d1, n1 = recipient_priv
  
    k = horner_pow(k1, d1, n1)
    s = horner_pow(s1, d1, n1)
  
    is_valid = Verify(k, s, sender_pub)
    return k, is_valid
  
def input_number(prompt):
    s = input(prompt).strip()
    try:
        return int(s, 16)
    except ValueError:
        return 0 
      
def input_public_key():
    e = input_number("Введіть e (відкритий експонент): ")
    n = input_number("Введіть n (модуль): ")
    return (e, n)
  
def input_private_key():
    d = input_number("Введіть d (секретний експонент): ")
    n = input_number("Введіть n (модуль): ")
    return (d, n)
  
def input_payload():
    k1 = input_number("Введіть k1: ")
    s1 = input_number("Введіть s1: ")
    return (k1, s1)
  
def interactive_mode():
    while True:
        print("\n=== Інтерактивний режим для тестування ===")
        print("1. Генерувати пару ключів")
        print("2. Шифрувати повідомлення")
        print("3. Розшифрувати шифротекст")
        print("4. Підписати повідомлення")
        print("5. Перевірити підпис")
        print("6. Надіслати ключ (SendKey)")
        print("7. Отримати ключ (ReceiveKey)")
        print("0. Вихід")
       
        choice = input("Виберіть операцію: ")
       
        if choice == '0':
            break
          
        elif choice == '1':
            bits = input_number("Введіть розмір в бітах (наприклад, 256): ")
            e = input_number("Введіть e (за замовчуванням 65537): ") or 65537
            label = input("Введіть мітку (A або B): ")
            print("Генерація p...")
          
            p, _ = generate_prime_with_rejects(bits)
            print("Генерація q...")
          
            q, _ = generate_prime_with_rejects(bits)
            GenerateKeyPair(p, q, e, label)
          
        elif choice == '2':
            message = input_number("Введіть повідомлення M: ")
            pub_key = input_public_key()
            c = Encrypt(message, pub_key)
          
            print(f"Шифротекст C = {hex(c)[2:].upper()}")
          
        elif choice == '3':
            ciphertext = input_number("Введіть шифротекст C: ")
            priv_key = input_private_key()
            m = Decrypt(ciphertext, priv_key)
          
            print(f"Розшифроване повідомлення M = {hex(m)[2:].upper()}")
          
        elif choice == '4':
            message = input_number("Введіть повідомлення M: ")
            priv_key = input_private_key()
            s = Sign(message, priv_key)
          
            print(f"Підпис S = {hex(s)[2:].upper()}")
          
        elif choice == '5':
            message = input_number("Введіть повідомлення M: ")
            signature = input_number("Введіть підпис S: ")
          
            pub_key = input_public_key()
            is_valid = Verify(message, signature, pub_key)
          
            print(f"Підпис вірний: {is_valid}")
          
        elif choice == '6':
            k = input_number("Введіть ключ k: ")
          
            sender_priv = input_private_key()
            recipient_pub = input_public_key()
          
            k1, s1 = SendKey(k, sender_priv, recipient_pub)
          
            print(f"Відправлено: k1 = {hex(k1)[2:].upper()}, s1 = {hex(s1)[2:].upper()}")
          
        elif choice == '7':
            payload = input_payload()
          
            recipient_priv = input_private_key()
            sender_pub = input_public_key()
          
            k_received, auth = ReceiveKey(payload, recipient_priv, sender_pub)
          
            print(f"Отриманий k: {hex(k_received)[2:].upper()}")
            print(f"Автентифікація: {auth}")
        else:
            print("Невірний вибір. Спробуйте ще раз.")
          
if __name__ == "__main__":
    bits = 256
    e_val = 65537
    max_rejects_show = 5
  
    print("\n=== Завдання 2: Генерація простих чисел (p, q для A; p1, q1 для B) ===")
    print("\nГенерація p для A:")
  
    p_A, rejected_p_A = generate_prime_with_rejects(bits, max_rejects_show)
    print(f"Знайдено просте p_A = {hex(p_A)[2:].upper()} ({p_A.bit_length()} біт)")
    print("Відкинуті кандидати (приклади):")
  
    for cand, reason in rejected_p_A:
        print(f" {hex(cand)[2:].upper()} — {reason}")
      
    print("\nГенерація q для A:")
    q_A, rejected_q_A = generate_prime_with_rejects(bits, max_rejects_show)
  
    print(f"Знайдено просте q_A = {hex(q_A)[2:].upper()} ({q_A.bit_length()} біт)")
    print("Відкинуті кандидати (приклади):")
    for cand, reason in rejected_q_A:
        print(f" {hex(cand)[2:].upper()} — {reason}")
      
    n_A_temp = p_A * q_A
    attempts = 0
    while True:
        attempts += 1
        print(f"\nСпроба {attempts} генерації для B:")
        print(" Генерація p1 для B:")
        p1_B, rejected_p1_B = generate_prime_with_rejects(bits, max_rejects_show)
      
        print(f" Знайдено просте p1_B = {hex(p1_B)[2:].upper()} ({p1_B.bit_length()} біт)")
        print(" Відкинуті кандидати (приклади):")
      
        for cand, reason in rejected_p1_B:
            print(f" {hex(cand)[2:].upper()} — {reason}")
          
        print(" Генерація q1 для B:")
        q1_B, rejected_q1_B = generate_prime_with_rejects(bits, max_rejects_show)
      
        print(f" Знайдено просте q1_B = {hex(q1_B)[2:].upper()} ({q1_B.bit_length()} біт)")
        print(" Відкинуті кандидати (приклади):")
      
        for cand, reason in rejected_q1_B:
            print(f" {hex(cand)[2:].upper()} — {reason}")
        n_B = p1_B * q1_B
      
        if n_B >= n_A_temp:
            print(f"Успіх після {attempts} спроб. Умова n_B ({n_B.bit_length()} біт) >= n_A ({n_A_temp.bit_length()} біт) виконана")
            break
        else:
            print(f"Спроба {attempts}: n_B ({n_B.bit_length()} біт) < n_A ({n_A_temp.bit_length()} біт), регенерація...")
    print("=" * 60)
  
    print("\n=== Завдання 3: Генерація ключів абонента A ===")
    pub_A, priv_A = GenerateKeyPair(p_A, q_A, e=e_val, label="A")
  
    print("\n=== Завдання 3: Генерація ключів абонента B ===")
    pub_B, priv_B = GenerateKeyPair(p1_B, q1_B, e=e_val, label="B")
    print("=" * 60)
  
    M = random.randint(1, min(pub_A[1], pub_B[1]) - 1)
    k = random.randint(1, pub_A[1] - 1)
  
    print(f"\n=== Завдання 4: Шифрування та розшифрування (для B як приклад) ===")
    print(f" Відкрите повідомлення M = {hex(M)[2:].upper()}")
    C = Encrypt(M, pub_B)
    print(f" Шифротекст C = {hex(C)[2:].upper()}")
    decrypted = Decrypt(C, priv_B)
  
    print(f" Розшифровано: {hex(decrypted)[2:].upper()} [{'OK' if decrypted == M else 'Помилка'}]")
  
    print(f"\n=== Завдання 4: Цифровий підпис та перевірка (для A як приклад) ===")
    print(f" Відкрите повідомлення M = {hex(M)[2:].upper()}")
    S = Sign(M, priv_A)
  
    print(f" Підпис S = {hex(S)[2:].upper()}")
    is_valid = Verify(M, S, pub_A)
  
    print(f" Підпис вірний: {is_valid} [{'OK' if is_valid else 'Помилка'}]")
    print(f"\n=== Завдання 5: Протокол конфіденційного розсилання ключів (A відправляє k до B) ===")
    print(f" Секретний ключ k (від A): {hex(k)[2:].upper()}")
    payload = SendKey(k, priv_A, pub_B)
  
    print(f" Відправлено: k1 = {hex(payload[0])[2:].upper()}, s1 = {hex(payload[1])[2:].upper()}")
    k_received, auth = ReceiveKey(payload, priv_B, pub_A)
  
    print(f" Отриманий k (B): {hex(k_received)[2:].upper()}")
    print(f" Автентифікація: {auth}")
    print(f" Збіг ключів: {k == k_received}")
  
    print(f" Результат: {'Успіх' if k == k_received and auth else 'Помилка'}")
  
    interactive_mode()
