import random
import math

def extended_gcd(a, b):
    """
    Розширений алгоритм Евкліда для знаходження НСД та коефіцієнтів Безу.
    
    Args:
        a (int): Перше число
        b (int): Друге число
        
    Returns:
        tuple: (gcd, u, v) де gcd - НСД(a,b), а u,v - коефіцієнти Безу: a*u + b*v = gcd
    """
    if a == 0:
        return b, 0, 1
    
    gcd, u1, v1 = extended_gcd(b % a, a)
    u = v1 - (b // a) * u1
    v = u1
    
    return gcd, u, v

def miller_rabin_test(n, k=20):
    """
    Тест Міллера-Рабіна на простоту числа.
    
    Args:
        n (int): Число для перевірки
        k (int): Кількість раундів тестування
        
    Returns:
        bool: True якщо число ймовірно просте, False якщо складене
    """
    # Перевірка тривіальних випадків
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Представляємо n-1 у вигляді d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Виконуємо k раундів тестування
    for _ in range(k):
        a = random.randint(2, n - 2)
        
        # Перевіряємо НСД(a, n)
        if math.gcd(a, n) != 1:
            return False
        
        # Обчислюємо a^d mod n
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        
        # Перевіряємо послідовність квадратів
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True

def generate_prime_number(bit_length=256):
    """
    Генерує просте число заданої довжини в бітах.
    
    Args:
        bit_length (int): Довжина числа в бітах
        
    Returns:
        int: Просте число
    """
    lower_bound = 1 << (bit_length - 1)  # 2^(bit_length-1)
    upper_bound = (1 << bit_length) - 1  # 2^bit_length - 1
    
    while True:
        candidate = random.randint(lower_bound, upper_bound)
        # Перевіряємо на простоту
        if miller_rabin_test(candidate):
            return candidate

def generate_rsa_key_pair(bit_length=256):
    """
    Генерує пару RSA ключів (відкритий та закритий).
    
    Args:
        bit_length (int): Довжина простих чисел в бітах
        
    Returns:
        tuple: (public_key, private_key) де:
            public_key = (n, e)
            private_key = (d, p, q)
    """
    # Генеруємо два різних простих числа
    p = generate_prime_number(bit_length)
    q = generate_prime_number(bit_length)
    while p == q:
        q = generate_prime_number(bit_length)
    
    # Обчислюємо модуль n
    n = p * q
    
    # Обчислюємо функцію Ейлера φ(n)
    phi_n = (p - 1) * (q - 1)
    
    # Вибираємо відкритий експонент e
    e = 65537  # Стандартне значення (2^16 + 1)
    if e >= phi_n:
        e = random.randint(2, phi_n - 1)
        while math.gcd(e, phi_n) != 1:
            e = random.randint(2, phi_n - 1)
    
    # Обчислюємо закритий експонент d
    d = pow(e, -1, phi_n)  # e * d ≡ 1 (mod φ(n))
    
    public_key = (n, e)
    private_key = (d, p, q)
    
    return public_key, private_key

def rsa_encrypt(message, public_key):
    """
    Шифрує повідомлення за допомогою відкритого ключа RSA.
    
    Args:
        message (int): Повідомлення для шифрування
        public_key (tuple): Відкритий ключ (n, e)
        
    Returns:
        int: Зашифроване повідомлення
    """
    n, e = public_key
    return pow(message, e, n)

def rsa_decrypt(ciphertext, private_key):
    """
    Розшифровує повідомлення за допомогою закритого ключа RSA.
    
    Args:
        ciphertext (int): Зашифроване повідомлення
        private_key (tuple): Закритий ключ (d, p, q)
        
    Returns:
        int: Розшифроване повідомлення
    """
    d, p, q = private_key
    n = p * q
    return pow(ciphertext, d, n)

def rsa_sign(message, private_key):
    """
    Створює цифровий підпис для повідомлення.
    
    Args:
        message (int): Повідомлення для підпису
        private_key (tuple): Закритий ключ (d, p, q)
        
    Returns:
        int: Цифровий підпис
    """
    return rsa_decrypt(message, private_key)

def rsa_verify(message, signature, public_key):
    """
    Перевіряє цифровий підпис.
    
    Args:
        message (int): Оригінальне повідомлення
        signature (int): Цифровий підпис
        public_key (tuple): Відкритий ключ (n, e)
        
    Returns:
        bool: True якщо підпис вірний, False якщо ні
    """
    n, e = public_key
    decrypted_signature = pow(signature, e, n)
    return message == decrypted_signature

def send_signed_message(message, sender_private_key, receiver_public_key):
    """
    Відправляє зашифроване повідомлення з цифровим підписом.
    
    Args:
        message (int): Повідомлення для відправки
        sender_private_key (tuple): Закритий ключ відправника
        receiver_public_key (tuple): Відкритий ключ отримувача
        
    Returns:
        tuple: (encrypted_message, encrypted_signature)
    """
    # Створюємо цифровий підпис
    signature = rsa_sign(message, sender_private_key)
    
    # Шифруємо повідомлення та підпис для отримувача
    encrypted_message = rsa_encrypt(message, receiver_public_key)
    encrypted_signature = rsa_encrypt(signature, receiver_public_key)
    
    return encrypted_message, encrypted_signature

def receive_signed_message(encrypted_message, encrypted_signature, 
                          sender_public_key, receiver_private_key):
    """
    Отримує та перевіряє зашифроване повідомлення з цифровим підписом.
    
    Args:
        encrypted_message (int): Зашифроване повідомлення
        encrypted_signature (int): Зашифрований підпис
        sender_public_key (tuple): Відкритий ключ відправника
        receiver_private_key (tuple): Закритий ключ отримувача
        
    Returns:
        bool: True якщо повідомлення автентичне, False якщо ні
    """
    # Розшифровуємо повідомлення та підпис
    decrypted_message = rsa_decrypt(encrypted_message, receiver_private_key)
    decrypted_signature = rsa_decrypt(encrypted_signature, receiver_private_key)
    
    # Перевіряємо цифровий підпис
    return rsa_verify(decrypted_message, decrypted_signature, sender_public_key)

def demonstrate_rsa_operations():
    """Демонстрація роботи RSA шифрування та цифрових підписів."""
    
    print("Генерація ключів для користувача A...")
    public_A, private_A = generate_rsa_key_pair()
    
    print("Генерація ключів для користувача B...")
    public_B, private_B = generate_rsa_key_pair()
    
    # Переконуємося, що n_A < n_B для коректного обміну
    if public_A[0] > public_B[0]:
        public_A, public_B = public_B, public_A
        private_A, private_B = private_B, private_A
        print("Ключі були обміняні для забезпечення n_A < n_B")
    
    print(f'\n=== КОРИСТУВАЧ A ===')
    print(f'Відкритий ключ:')
    print(f'  n = {public_A[0]}')
    print(f'  e = {public_A[1]}')
    print(f'Закритий ключ:')
    print(f'  d = {private_A[0]}')
    print(f'  p = {private_A[1]}')
    print(f'  q = {private_A[2]}')
    
    print(f'\n=== КОРИСТУВАЧ B ===')
    print(f'Відкритий ключ:')
    print(f'  n = {public_B[0]}')
    print(f'  e = {public_B[1]}')
    print(f'Закритий ключ:')
    print(f'  d = {private_B[0]}')
    print(f'  p = {private_B[1]}')
    print(f'  q = {private_B[2]}')
    
    # Тестування шифрування/розшифрування
    print(f'\n=== ТЕСТУВАННЯ ШИФРУВАННЯ ===')
    message = random.randint(1, min(public_A[0], public_B[0]) - 1)
    print(f'Оригінальне повідомлення: {message}')
    
    # Шифрування та розшифрування для користувача A
    ciphertext = rsa_encrypt(message, public_A)
    decrypted = rsa_decrypt(ciphertext, private_A)
    print(f'Зашифроване повідомлення: {ciphertext}')
    print(f'Розшифроване повідомлення: {decrypted}')
    print(f'Шифрування коректне: {message == decrypted}')
    
    # Тестування цифрових підписів
    print(f'\n=== ТЕСТУВАННЯ ЦИФРОВИХ ПІДПИСІВ ===')
    signature = rsa_sign(message, private_A)
    verification = rsa_verify(message, signature, public_A)
    print(f'Цифровий підпис: {signature}')
    print(f'Перевірка підпису: {verification}')
    
    # Тестування безпечного обміну повідомленнями
    print(f'\n=== БЕЗПЕЧНИЙ ОБМІН ПОВІДОМЛЕННЯМИ ===')
    print(f'Повідомлення для обміну: {message}')
    
    # Користувач A відправляє повідомлення користувачу B
    encrypted_msg, encrypted_sig = send_signed_message(
        message, private_A, public_B
    )
    print(f'Зашифроване повідомлення: {encrypted_msg}')
    print(f'Зашифрований підпис: {encrypted_sig}')
    
    # Користувач B отримує та перевіряє повідомлення
    is_authentic = receive_signed_message(
        encrypted_msg, encrypted_sig, public_A, private_B
    )
    print(f'Повідомлення автентичне: {is_authentic}')
    
    return is_authentic

if __name__ == '__main__':
    # Запускаємо демонстрацію
    success = demonstrate_rsa_operations()
    
    if success:
        print(f'\n Всі операції RSA виконані успішно!')
    else:
        print(f'\n Сталася помилка при виконанні операцій RSA')