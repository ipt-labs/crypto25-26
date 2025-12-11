"""
Модуль криптосистеми RSA
Варіант 6
"""

from dataclasses import dataclass
from arithmetic_ops import fast_power_mod, compute_mod_inverse, find_gcd
from prime_generation import generate_safe_prime_pair


@dataclass
class RSAKeyPair:
    """Структура для зберігання пари ключів RSA"""
    public_key: tuple[int, int]  # (e, n)
    private_key: tuple[int, int, int]  # (d, p, q)
    
    def __repr__(self):
        e, n = self.public_key
        d, p, q = self.private_key
        return (f"RSAKeyPair(\n"
                f"  public=(e={e}, n={n} ({n.bit_length()} bits)),\n"
                f"  private=(d={d}, p={p}, q={q})\n"
                f")")


def GenerateKeyPair(bits: int = 512, public_exponent: int = 65537) -> RSAKeyPair:
    """
    Генерація пари ключів RSA
    
    Args:
        bits: бітова довжина модуля n (буде згенеровано два простих по bits//2 біт)
              Рекомендується мінімум 512 біт, для реальних систем 2048+ біт
        public_exponent: відкрита експонента e (за замовчуванням 65537 = 2^16 + 1)
    
    Returns:
        RSAKeyPair з відкритим та секретним ключами
    """
    if bits < 32:
        raise ValueError("Бітова довжина має бути мінімум 32")
    
    # Генеруємо два простих числа p та q
    half_bits = bits // 2
    p, q = generate_safe_prime_pair(half_bits)
    
    # Обчислюємо модуль n та функцію Ойлера φ(n)
    n = p * q
    phi_n = (p - 1) * (q - 1)
    
    # Перевіряємо чи e взаємно просте з φ(n)
    e = public_exponent
    if find_gcd(e, phi_n) != 1:
        raise ValueError(f"Публічна експонента e={e} не взаємно проста з φ(n)")
    
    # Обчислюємо секретну експоненту d
    d = compute_mod_inverse(e, phi_n)
    
    return RSAKeyPair(
        public_key=(e, n),
        private_key=(d, p, q)
    )


def Encrypt(plaintext: int, public_exponent: int, modulus: int) -> int:
    """
    Шифрування повідомлення за допомогою RSA

    Args:
        plaintext: відкрите повідомлення M (0 <= M < n)
        public_exponent: відкрита експонента e
        modulus: модуль n

    Returns:
        ciphertext: зашифроване повідомлення C = M^e mod n
    """
    if plaintext < 0 or plaintext >= modulus:
        raise ValueError(f"Повідомлення має бути в діапазоні [0, {modulus-1}]")
    
    return fast_power_mod(plaintext, public_exponent, modulus)


def Decrypt(ciphertext: int, private_exponent: int, modulus: int) -> int:
    """
    Розшифрування повідомлення за допомогою RSA

    Args:
        ciphertext: зашифроване повідомлення C
        private_exponent: секретна експонента d
        modulus: модуль n

    Returns:
        plaintext: відкрите повідомлення M = C^d mod n
    """
    if ciphertext < 0 or ciphertext >= modulus:
        raise ValueError(f"Шифротекст має бути в діапазоні [0, {modulus-1}]")
    
    return fast_power_mod(ciphertext, private_exponent, modulus)


def Sign(message: int, private_exponent: int, modulus: int) -> tuple[int, int]:
    """
    Створення цифрового підпису RSA

    Args:
        message: повідомлення M для підпису
        private_exponent: секретна експонента d
        modulus: модуль n

    Returns:
        (message, signature): пара (M, S) де S = M^d mod n
    """
    if message < 0 or message >= modulus:
        raise ValueError(f"Повідомлення має бути в діапазоні [0, {modulus-1}]")
    
    signature = fast_power_mod(message, private_exponent, modulus)
    return (message, signature)


def Verify(message: int, signature: int, public_exponent: int, modulus: int) -> bool:
    """
    Перевірка цифрового підпису RSA

    Args:
        message: повідомлення M
        signature: підпис S
        public_exponent: відкрита експонента e
        modulus: модуль n

    Returns:
        True якщо підпис вірний (M == S^e mod n), False інакше
    """
    if message < 0 or message >= modulus:
        return False
    
    recovered = fast_power_mod(signature, public_exponent, modulus)
    return message == recovered


def SendKey(secret_key: int, 
           sender_private_exp: int, sender_modulus: int,
           receiver_public_exp: int, receiver_modulus: int) -> tuple[int, int]:
    """
    Підготовка ключа для відправки з підписом (протокол розсилання ключів)
    Відправник А відправляє ключ k отримувачу B

    Args:
        secret_key: секретний ключ k для передачі
        sender_private_exp: секретна експонента d відправника А
        sender_modulus: модуль n відправника А
        receiver_public_exp: відкрита експонента e1 отримувача B
        receiver_modulus: модуль n1 отримувача B

    Returns:
        (k1, S1): зашифрований ключ та підпис
        де k1 = k^e1 mod n1, S1 = S^e1 mod n1, S = k^d mod n

    Raises:
        ValueError: якщо n > n1 (порушення умови протоколу)
    """
    if sender_modulus > receiver_modulus:
        raise ValueError("Модуль відправника має бути <= модуля отримувача")
    
    # Підписуємо ключ секретним ключем відправника
    _, signature = Sign(secret_key, sender_private_exp, sender_modulus)
    
    # Шифруємо ключ та підпис відкритим ключем отримувача
    encrypted_key = Encrypt(secret_key, receiver_public_exp, receiver_modulus)
    encrypted_signature = Encrypt(signature, receiver_public_exp, receiver_modulus)
    
    return (encrypted_key, encrypted_signature)


def ReceiveKey(encrypted_key: int, encrypted_signature: int,
              receiver_private_exp: int, receiver_modulus: int,
              sender_public_exp: int, sender_modulus: int) -> tuple[int, int, bool]:
    """
    Отримання та перевірка ключа (протокол розсилання ключів)
    Отримувач B отримує ключ від відправника А

    Args:
        encrypted_key: зашифрований ключ k1
        encrypted_signature: зашифрований підпис S1
        receiver_private_exp: секретна експонента d1 отримувача B
        receiver_modulus: модуль n1 отримувача B
        sender_public_exp: відкрита експонента e відправника А
        sender_modulus: модуль n відправника А

    Returns:
        (key, signature, verified): розшифрований ключ k, підпис S та результат перевірки
    """
    # Розшифровуємо ключ та підпис секретним ключем отримувача
    key = Decrypt(encrypted_key, receiver_private_exp, receiver_modulus)
    signature = Decrypt(encrypted_signature, receiver_private_exp, receiver_modulus)
    
    # Перевіряємо підпис відкритим ключем відправника
    verified = Verify(key, signature, sender_public_exp, sender_modulus)
    
    return (key, signature, verified)
