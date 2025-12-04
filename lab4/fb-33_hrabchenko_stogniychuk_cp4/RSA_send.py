from RSA_key import generate_rsa_keys
from random_prime import generate_prime_pairs
from RSA import RSA_Encrypt, RSA_Decrypt, RSA_Sign, RSA_Verify
import random

def RSA_SendKey(k, public_key_b, private_key_a):
    """
    Реалізація роботи відправника A.
    public_key_b: відкритий ключ абонента B (n1, e1)
    private_key_a: секретний ключ абонента A (d, p, q)
    """
    k1 = RSA_Encrypt(k, public_key_b)   # k1 = k^e1 mod n1
    S = RSA_Sign(k, private_key_a)      # S = k^d mod n
    S1 = RSA_Encrypt(S, public_key_b)   # S1 = S^e1 mod n1

    return k1, S1

def RSA_ReceiveKey(k1, S1, private_key_b, public_key_a):
    """
    Реалізація роботи приймача B.
    k1: зашифроване значення k
    S1: зашифрований підпис S
    private_key_b: секретний ключ абонента B (d1, p1, q1)
    public_key_a: відкритий ключ абонента A (n, e)
    """
    k_dec = RSA_Decrypt(k1, private_key_b)  # k = k1^d1 mod n1
    S_dec = RSA_Decrypt(S1, private_key_b)  # S = S1^d1 mod n1

    k_verify = RSA_Verify(S_dec, public_key_a, k_dec)  # Перевірка підпису

    return k_dec, k_verify

def main():
    bit_length = 256
    
    # Генерація простих чисел для абонента A
    primes_a = generate_prime_pairs(bit_length)
    p, q = primes_a[0][0], primes_a[0][1]

    # Генерація простих чисел для абонента B
    primes_b = generate_prime_pairs(bit_length)
    p1, q1 = primes_b[0][0], primes_b[0][1]

    # Генерація ключів для абонентів A і B
    public_key_a, private_key_a = generate_rsa_keys(p, q)
    public_key_b, private_key_b = generate_rsa_keys(p1, q1)

    # Вибираємо випадкове значення k
    _, n = public_key_a
    k = random.randint(1, n - 1)  # 0 < k < n

    # Відправник A шле ключ
    k1, S1 = RSA_SendKey(k, public_key_b, private_key_a)

    # Приймач B отримує ключ
    k_dec, k_verify = RSA_ReceiveKey(k1, S1, private_key_b, public_key_a)

    # Вивід результатів
    print(f"Оригінальний k: {k}")
    print(f"Розшифрований абонентом B k: {k_dec}")
    print(f"Перевірка підпису А пройшла успішно: {k_verify}")
    print(f"Перевірка відповідності ключів: {'Успішно' if k == k_dec else 'Неуспішно'}")

if __name__ == "__main__":
    main()
