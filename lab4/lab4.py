# This script has no specific requirements
from math import sqrt
import random
import hashlib

def gcd(a, b):
    while b > 0:
        # q = a // b
        r = a % b
        a, b = b, r
    return a

def find_inverse_element(a, m):
    # r=a*u+m*v, u - коефіцієнт біля a, v - коефіцієнт біля m
    u0, u1 = 0, 1 
    v0, v1 = 1, 0

    m_init = m # зберігаємо значення модуля перед перевизначенням в операціях
    while a > 0:
        q = m // a # 13/5 = 2
        r = m % a # 13 - 2 * 5 = 3
        # -> 13 = 2 * 5 + 3

        m, a = a, r # 5, 2 (наступний крок, зносимо a і r)

        next_u0 = u1
        next_v0 = v1
        # 3 = (13*0 + 5*1) - 2*(13*1 + 5*0)
        u1= u0 - q * u1 #0 -2*1 = -2, коеф. біля a
        v1 = v0 - q* v1 # 1-2*0 = 1, коеф. біля m
        # 3 = -2 * 5 + 1 * 13

        # оновлюємо початкові коефіцієнти для наступного кроку
        u0, v0 = next_u0, next_v0

    if m != 1:
        return None
    else:
        return u0 % m_init # повертаємо коеф. біля a за модулем m (u0, тому що останній крок 0 = u*0 +v*m, а треба 1=ua+vm)

def GenSmallPrimes(limit=1000):
    isPrime = [True] * (limit + 1)

    # Решето Ератосфена
    primes = []
    t = int(sqrt(limit))
    for i in range(2, limit + 1):
        if isPrime[i]:
            primes.append(i)

            if i <= t: # стільки ітерацій достатньо, щоб викреслити всі складені
                for j in range(i*i, limit + 1, i):
                    isPrime[j] = False # викреслюємо кратні

    return primes

def num_to_digits(n):
    n_digits = []
    for ch in str(n):
        n_digits.append(int(ch))

    return n_digits

def divisible_pascal(p, b, m):
    r = 1
    mod_sum = 0
    p_digits = num_to_digits(p)
    p_digits = p_digits[::-1]

    for a in p_digits:
        mod_sum = (mod_sum + a * r) % m
        r = (r * b) % m

    return mod_sum == 0

def is_prime_trial(p, small_primes):
    if p < 2:
        return False
    if p in small_primes:
        return True
    
    b = 10
    for sp in small_primes:
        if sp**2 > p: # немає сенсу далі перевіряти, очевидно, що число - просте
            break

        if divisible_pascal(p, b, sp):  
            return False

    return True

def mod_gorner(a, n, m): # (a^n) modm
    b = 1
    highest_bit = n.bit_length() - 1
    a = a % m

    for i in range(highest_bit, -1, -1): # k-1 to 0
        b = (b**2) % m

        if (n >> i) & 1:
            b = (b * a) % m # домножуємо на a, якщо біт - 1

    return b

def find_d_s(p):
    d = p - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    return d, s

def is_strong_pseudoprime(a, p, d, s):
    x = mod_gorner(a, d, p) # (a^d) modp

    if x == 1:
        return True

    # a^(d * 2^r) = -1 modp
    for _ in range(0, s): # r < s
        if x == p - 1:
            return True
        
        x = (x ** 2) % p # r++

    return False

def miller_rabin_test(p, k, small_primes):
    if not is_prime_trial(p, small_primes):
        print(f"Число не пройшло тест пробних ділень\n")
        return False
    
    d, s = find_d_s(p)

    for _ in range(k):
        a = random.randrange(2, p - 1)

        if gcd(a, p) != 1:
            return False
        
        if not is_strong_pseudoprime(a, p, d, s):
            print(f"Число не є псевдопростим за основою {a}\n")
            return False

    return True

# 2^255 <= p < 2^256 - 256-bit prime (1 << 255 <= p <= (1 << 256) - 1)
# k = 15 => e = 4^-15 = 9,3 * 10^-10, e < 10^-9
def RandPrime(small_primes, n0 = 1 << 255, n1 = (1 << 256) - 1, k = 15):
    while True:
        x = random.randrange(n0, n1)

        if x % 2 == 0:
            m0 = x + 1
        else:
            m0 = x

        max_i = (n1 - m0) // 2
        for i in range(max_i + 1):
            p = m0 + 2 * i
            print(f"Згенеровано число: {p}")

            if miller_rabin_test(p, k, small_primes):
                e = 4 ** (-k)
                print(f"\nЧисло {p} прошло тест Міллера-Рабіна з {k} ітераціями\nПохибка: {e:.1e}")
                print("\n", "-"*100, "\n")
                return p

def GenKeyPair(p, q):
    n = p * q
    fn = (p-1)*(q-1)
    
    while True:
        e = random.randrange(2, fn - 1)
        if gcd(e, fn) == 1:
            break

    d = find_inverse_element(e, fn)

    pk = (n, e)
    sk = (d, p, q)

    return pk, sk

def str_to_int(msg: str) -> int:
    text_bytes = msg.encode()
    number = int.from_bytes(text_bytes, "big")
    return number

def int_to_str(num: int) -> str:
    byte_len = (num.bit_length() + 7) // 8
    text_bytes = num.to_bytes(byte_len, "big")
    try:
        text = text_bytes.decode()
        return text
    except UnicodeDecodeError:
        return num

def Encrypt(m, pk):
    m_type = None
    if isinstance(m, str):
        m_int = str_to_int(m)

    elif isinstance(m, int):
        if m>=0:
            m_int = m
            m_type = "int"
        else:
            m_int = str_to_int(str(m))

    else:
        try:
            m_int = str_to_int(str(m))
        except:
            return None

    n, e = pk
    print(f"msg in int format: {m_int}")
    c = mod_gorner(m_int, e, n)
    print(f"Encrypted: {c}")

    return c, m_type

def Decrypt(c, sk, m_type=None):
    if not isinstance(c, int) or c < 0:
        print("failed decrypt: it is not ciphertext")
        return None
    
    d, p, q = sk
    n = p * q
    m = mod_gorner(c, d, n)
    if m_type == None:
        m = int_to_str(m)
        
    print(f"Decrypted: {m}")
    return m

def HashMsg(msg):
    if isinstance(msg, str):
        msg_bytes = msg.encode()
    elif isinstance(msg, int):
        byte_len = (msg.bit_length() + 7) // 8
        msg_bytes = msg.to_bytes(byte_len, "big")
    else:
        try:
            msg_bytes = str(msg).encode()
        except:
            return None

    digest_hash = hashlib.sha256(msg_bytes).digest()
    digest_int = int.from_bytes(digest_hash, "big")
    print(f"Hash: {digest_int}")
    return digest_int

def Sign(m, sk):
    d, p, q = sk
    n = p * q

    h = HashMsg(m)
    s = mod_gorner(h, d, n)
    print(f"Sign: {s}")

    return s

def Verify(packet, pk):
    m, s = packet
    n, e = pk

    h = HashMsg(m)
    recovered_h = mod_gorner(s, e, n)
    if (recovered_h == h):
        print("Повідомлення і підпис співпадають")
    else:
        print("Повідомлення і підпис не співпадають")
    return recovered_h == h

def send(msg, sk_A, pk_B):
    print(f"Sending message: '{msg}'...")
    enc_msg, msg_type = Encrypt(msg, pk_B)
    sign_msg = Sign(msg, sk_A)

    packet = (enc_msg, sign_msg, msg_type)

    return packet

def recv(packet, sk_B, pk_A):
    enc_msg, sign_msg, msg_type = packet
    dec_msg = Decrypt(enc_msg, sk_B, msg_type)

    if dec_msg:
        packet = (dec_msg, sign_msg)
        verified = Verify(packet, pk_A)
        if verified:
            return dec_msg
        else:
            return "message compromised"
        
    return "failed to decrypt"

def SendKey(sk_A, pk_A, pk_B):
    nA, _ = pk_A
    nB, _ = pk_B

    while nB<nA:
        print("Перегенерація пари ключів відправника для коректної роботи протоколу конфіденційного розсилання ключів\n")
        small_primes = GenSmallPrimes()
        n0 = 1 << 255
        n1 = (1 << 256) - 1
        p3  = RandPrime(small_primes, n0, n1)
        q3  = RandPrime(small_primes, n0, n1)
        nA = p3 * q3
        pk_A, sk_A = GenKeyPair(p3, q3)

    k = random.randrange(1, nA-1)
    print(f"Created key: {k}")

    k1, _ = Encrypt(k, pk_B)
    s = Sign(k, sk_A)
    s1, _ = Encrypt(s, pk_B)

    return (k1, s1), k, pk_A, sk_A            

def RecvKey(packet, sk_B, pk_A):
    k1,s1 = packet

    k = Decrypt(k1, sk_B, m_type="int")
    s = Decrypt(s1, sk_B, m_type="int")

    packet = (k, s)
    verified = Verify(packet, pk_A)

    if verified:
        return k
    else:
        return "message compromised"

def main():
    small_primes = GenSmallPrimes()
    # 2^255 <= p < 2^256 - 256 бітне число
    n0 = 1 << 255
    n1 = (1 << 256) - 1

    p1  = RandPrime(small_primes, n0, n1)
    q1  = RandPrime(small_primes, n0, n1)

    p2 = RandPrime(small_primes, n0, n1)
    q2 = RandPrime(small_primes, n0, n1)

    if p1 * q1 <= p2 * q2:
        p_A, q_A, p_B, q_B = p1, q1, p2, q2
    else:
         p_B, q_B, p_A, q_A = p1, q1, p2, q2
    
    print(f"p_A: {p_A} \nq_A: {q_A}\n\np_B: {p_B} \nq_B: {q_B}")
    print("\n", "-"*100, "\n")

    pk_A, sk_A = GenKeyPair(p_A, q_A)
    pk_B, sk_B = GenKeyPair(p_B, q_B)
    n_A, e_A = pk_A
    n_B, e_B = pk_B
    d_A, _, _ = sk_A
    d_B, _, _ = sk_B
    print(f"n_A: {n_A} \ne_A: {e_A}\nd_A: {d_A}\n\nn_B: {n_B} \ne_B: {e_B} \nd_B: {d_B}")
    print("\n", "-"*100, "\n")

    # Протокол обміну шифрованих повідомлень з цифровим підписом
    print("A send number to B")
    n, _ = pk_A
    msg = random.randrange(1, n-1)
    packet1 = send(msg, sk_A, pk_B)

    print("\nA send text to B")
    text_msg = "I'm A"
    packet2 = send(text_msg, sk_A, pk_B)

    print("\nB recv number from A")
    r_msg1 = recv(packet1, sk_B, pk_A)
    print(f"recieved message {r_msg1}\n")

    print("nB recv text from A")
    r_msg2 = recv(packet2, sk_B, pk_A)
    print(f"recieved message {r_msg2}\n")

    print("B send number to A")
    packet3 = send(msg, sk_A, pk_B)

    print("\nA recv number from B")
    r_msg3 = recv(packet3, sk_B, pk_A)
    print(f"recieved message {r_msg3}")
    
    # Протокол конфіденційного розсилання ключів 
    print("\n", "-"*100, "\n")
    print("A send key to B")
    packet4, k1, pk_A, sk_A = SendKey(sk_A, pk_A, pk_B)
    print(f"sender saved key: {k1}\n")
    r_msg4 = RecvKey(packet4, sk_B, pk_A)
    print(f"reciever recieved key {r_msg4}\n")

    print("B send key to A")
    packet5, k2, pk_B, sk_B = SendKey(sk_B, pk_B, pk_A)
    print(f"sender saved key: {k2}\n")
    r_msg5 = RecvKey(packet5, sk_A, pk_B)
    print(f"reciever recieved key {r_msg5}")

if __name__ == "__main__":
    main()
